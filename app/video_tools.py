"""Video generation tool using gemini-omni-flash-preview model with GCS upload and ADK Artifact saving."""

import base64
import time
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

# Hardcoded constants as required
GCS_BUCKET_NAME = "oracle-sql-copilot-qwiklabs-gcp-02-56893539409e"
GCP_PROJECT_ID = "qwiklabs-gcp-02-56893539409e"


def generate_sql_concept_video(prompt: str, tool_context: ToolContext = None) -> dict:
    """Generates a short animated video visualizing Oracle database concepts, query execution flows, or data architectures.

    Args:
        prompt: Description of the video to generate (e.g. '3D animation of Oracle CBO query optimizer selecting an index scan vs full table scan', 'Data flowing through table joins').
        tool_context: ADK ToolContext automatically injected by the framework.

    Returns:
        A dictionary containing the public Cloud Storage HTTPS URL (https://storage.googleapis.com/<bucket>/<object>), filename, and status.
    """
    if not prompt or not prompt.strip():
        return {"error": "Prompt for video generation cannot be empty."}

    try:
        genai_client = genai.Client(
            vertexai=True,
            project=GCP_PROJECT_ID,
            location="global",
        )

        full_prompt = f"3D motion graphic animation visualizing Oracle database topic: {prompt}"
        response = genai_client.interactions.create(
            model="gemini-omni-flash-preview",
            input=full_prompt,
        )

        video_bytes = None
        if hasattr(response, "output_video") and response.output_video and getattr(response.output_video, "data", None):
            video_bytes = base64.b64decode(response.output_video.data)
        elif hasattr(response, "steps") and response.steps:
            for step in response.steps:
                if hasattr(step, "content") and step.content:
                    for part in step.content:
                        if getattr(part, "type", None) == "video" and getattr(part, "data", None):
                            video_bytes = base64.b64decode(part.data)
                            break

        if not video_bytes:
            return {"error": "Video generation completed but no video bytes were returned by the model."}

        filename = f"concept_video_{int(time.time())}.mp4"
        mime_type = "video/mp4"

        # (1) Save artifact via tool_context so it appears in Playground Artifacts panel
        if tool_context is not None:
            try:
                artifact_part = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
                tool_context.save_artifact(filename=filename, artifact=artifact_part)
            except Exception as e:
                print(f"Warning: Failed to save video artifact in tool_context: {e}")

        # (2) Upload video bytes directly to public Cloud Storage bucket without writing local file
        storage_client = storage.Client(project=GCP_PROJECT_ID)
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(video_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{filename}"

        return {
            "status": "SUCCESS",
            "filename": filename,
            "public_url": public_url,
            "message": f"Successfully generated concept video and published to Cloud Storage: {public_url}",
        }

    except Exception as e:
        return {"error": f"Error generating concept video: {str(e)}"}
