import os
from typing import Optional, List
from uuid import uuid4 as uuid
from google import genai
from google.genai import types
from google.genai.types import GenerateContentConfigOrDict, GenerateContentResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from app.clipping.domain.video_understanding import (
    VideoUnderstandingService,
    HighlightsResponse,
)
from app.clipping.domain.video_understanding import Highlight

load_dotenv()

GOOGLE_GENAI_API_KEY = os.getenv("GOOGLE_GENAI_API_KEY")
MODEL_NAME = "models/gemini-2.5-flash"


class VideoUnderstandingHighlight(BaseModel):
    start_time: Optional[str]  # e.g. "00:15"
    end_time: Optional[str]  # e.g. "00:45"
    description: Optional[str]


class VideoUnderstandingHighlightsResponse(BaseModel):
    highlights: List[VideoUnderstandingHighlight]


class GeminiVideoUnderstandingService(VideoUnderstandingService):
    def analyze_video_highlights(
        self, video_url: str, prompt: Optional[str] = None
    ) -> HighlightsResponse:

        if not GOOGLE_GENAI_API_KEY:
            raise RuntimeError("GOOGLE_GENAI_API_KEY is not set in environment.")

        client = genai.Client(api_key=GOOGLE_GENAI_API_KEY)

        system_prompt = prompt or (
            "Find and summarize the highlights (best moments) of this video. "
            "Return a list of highlights with start_time, end_time, and a short description for each."
        )

        contents = types.Content(
            parts=[
                types.Part(file_data=types.FileData(file_uri=video_url)),
                types.Part(text=system_prompt),
            ]
        )

        config: GenerateContentConfigOrDict = {
            "response_mime_type": "application/json",
            "response_schema": VideoUnderstandingHighlightsResponse,
        }

        response: GenerateContentResponse = client.models.generate_content(  # type: ignore
            model=MODEL_NAME, contents=contents, config=config
        )

        if hasattr(response, "parsed"):
            try:
                parsed = response.parsed
                if isinstance(parsed, VideoUnderstandingHighlightsResponse):
                    return self.transform_to_response_highlights(parsed.highlights)
                if isinstance(parsed, dict):
                    return self.transform_to_response_highlights(VideoUnderstandingHighlightsResponse(**parsed).highlights)
            except Exception:
                return HighlightsResponse(highlights=[])
        return HighlightsResponse(highlights=[])

    def transform_to_response_highlights(
        self, highlights: list[VideoUnderstandingHighlight]
    ) -> HighlightsResponse:
        return HighlightsResponse(
            highlights=[
                Highlight(
                    id=str(uuid()),
                    start_time=h.start_time,
                    end_time=h.end_time,
                    description=h.description,
                )
                for h in highlights
            ]
        )
