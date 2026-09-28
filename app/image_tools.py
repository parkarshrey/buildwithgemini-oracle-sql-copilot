"""Image generation tool using gemini-3.1-flash-lite-image model with GCS upload and ADK Artifact saving."""

import time
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

# Hardcoded constants as required
GCS_BUCKET_NAME = "oracle-sql-copilot-qwiklabs-gcp-02-56893539409e"
GCP_PROJECT_ID = "qwiklabs-gcp-02-56893539409e"


def generate_sql_diagram_image(prompt: str, tool_context: ToolContext = None) -> dict:
    """Generates a technical visual diagram (ERD, architecture, execution plan) for Oracle SQL items.

    Args:
        prompt: Description of the visual diagram to generate (e.g., 'ERD diagram for sales and orders tables', 'Oracle CBO execution plan flowchart').
        tool_context: ADK ToolContext automatically injected by the framework.

    Returns:
        A dictionary containing the public Cloud Storage HTTPS URL, filename, and status.
    """
    if not prompt or not prompt.strip():
        return {"error": "Prompt for image generation cannot be empty."}

    try:
        # Initialize Google GenAI Client with vertexai in global region
        genai_client = genai.Client(
            vertexai=True,
            project=GCP_PROJECT_ID,
            location="global",
        )

        full_prompt = f"Technical vector-style database architecture diagram for Oracle SQL: {prompt}"
        response = genai_client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=full_prompt,
            config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
        )

        image_bytes = None
        mime_type = "image/png"
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    image_bytes = part.inline_data.data
                    mime_type = part.inline_data.mime_type or "image/png"
                    break

        if not image_bytes:
            return {"error": "Image generation completed but no image bytes were returned by the model."}

        ext = "jpg" if "jpeg" in mime_type.lower() or "jpg" in mime_type.lower() else "png"
        filename = f"diagram_{int(time.time())}.{ext}"

        # (1) Save artifact via tool_context so it appears in Playground Artifacts panel
        if tool_context is not None:
            try:
                artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
                tool_context.save_artifact(filename=filename, artifact=artifact_part)
            except Exception as e:
                print(f"Warning: Failed to save artifact in tool_context: {e}")

        # (2) Upload image bytes directly to public Cloud Storage bucket without writing local file
        storage_client = storage.Client(project=GCP_PROJECT_ID)
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{filename}"

        return {
            "status": "SUCCESS",
            "filename": filename,
            "public_url": public_url,
            "message": f"Successfully generated diagram image and published to Cloud Storage: {public_url}",
        }

    except Exception as e:
        return {"error": f"Error generating diagram image: {str(e)}"}
