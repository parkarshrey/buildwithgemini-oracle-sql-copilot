# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


import json
from pathlib import Path
from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from google.adk.agents.callback_context import CallbackContext
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.memory import VertexAiMemoryBankService
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from .a2ui_utils import a2ui_callback
from .community_tools import search_oracle_community_solutions
from .firestore_tools import (
    get_saved_query_by_id,
    list_saved_queries,
    save_sql_query,
)
from .image_tools import generate_sql_diagram_image
from .maps_tools import find_nearby_places, geocode_address
from .sql_tools import parse_and_lint_sql
from .video_tools import generate_sql_concept_video

MEMORY_BANK_ID = "246983296947322880"
GCP_PROJECT_ID = "701008191527"
GCP_LOCATION = "us-east1"


async def generate_memories_callback(callback_context: CallbackContext):
    """WRITE callback: sends session events to Vertex AI Memory Bank after each turn."""
    try:
        await callback_context.add_session_to_memory()
    except Exception as e:
        import logging
        logging.warning(f"Memory service unavailable for session: {e}")
    return None


def memory_bank_service_builder():
    """Builds VertexAiMemoryBankService targeting the deployed Agent Engine Memory Bank."""
    return VertexAiMemoryBankService(
        project=GCP_PROJECT_ID,
        location=GCP_LOCATION,
        agent_engine_id=MEMORY_BANK_ID,
    )


def _create_code_executor():
    metadata_path = Path(__file__).parent.parent / "deployment_metadata.json"
    sandbox_id = None
    agent_engine_id = None

    if metadata_path.exists():
        try:
            with open(metadata_path, "r") as f:
                meta = json.load(f)
                sandbox_id = meta.get("sandbox_resource_name")
                agent_engine_id = meta.get("remote_agent_runtime_id")
        except Exception as e:
            print(f"Warning: Could not read deployment_metadata.json: {e}")

    if sandbox_id:
        return AgentEngineSandboxCodeExecutor(sandbox_resource_name=sandbox_id)
    elif agent_engine_id:
        return AgentEngineSandboxCodeExecutor(agent_engine_resource_name=agent_engine_id)
    else:
        return AgentEngineSandboxCodeExecutor()


schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are Oracle SQL Copilot & Advisor, an expert AI assistant for data engineers "
        "and database developers. You help users generate, explain, optimize, and debug "
        "Oracle SQL queries. You strictly remember and adhere to all stated user preferences, "
        "personal details, and health/dietary allergies across all conversations using Vertex AI Memory Bank. "
        "You can execute Python code snippets in a secure Agent Engine sandbox to verify math/logic. "
        "Always use the parse_and_lint_sql tool when asked to parse, format, lint, or analyze a SQL query. "
        "Use search_oracle_community_solutions to look up real developer discussions for Oracle SQL errors. "
        "Use generate_sql_diagram_image to create visual database ERD diagrams. Use generate_sql_concept_video "
        "to generate 3D animated videos for database concepts and execution flows. You can also save queries "
        "to and search queries from the Firestore catalog, geocode addresses, and find nearby places."
    ),
    workflow_description="Analyze the request and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no preamble, no markdown code blocks, no text before or after the JSON, and never wrap it in <a2a_datapart_json> or <a2ui-json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    code_executor=_create_code_executor(),
    instruction=instruction,
    tools=[
        PreloadMemoryTool(),
        get_weather,
        get_current_time,
        save_sql_query,
        list_saved_queries,
        get_saved_query_by_id,
        parse_and_lint_sql,
        search_oracle_community_solutions,
        geocode_address,
        find_nearby_places,
        generate_sql_diagram_image,
        generate_sql_concept_video,
    ],
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
