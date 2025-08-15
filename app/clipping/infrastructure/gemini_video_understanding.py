import os
from typing import Optional, List, Literal
from uuid import uuid4 as uuid
from google import genai
from google.genai import types
from google.genai.types import (
    GenerateContentConfigOrDict,
    GenerateContentResponse,
    MediaResolution,
)
from pydantic import BaseModel, Field, model_validator
from dotenv import load_dotenv
from app.clipping.domain.video_understanding import (
    VideoUnderstandingService,
    HighlightsResponse,
)
from app.clipping.domain.video_understanding import Highlight

load_dotenv()

GOOGLE_GENAI_API_KEY = os.getenv("GOOGLE_GENAI_API_KEY")
MODEL_NAME = "models/gemini-2.5-flash"


def parse_timestamp_fn(timestamp: str, time_format: Literal["HH:MM:SS", "MM:SS"]):
    if time_format == "HH:MM:SS":
        hours, minutes, seconds = map(int, timestamp.split(":"))
    elif time_format == "MM:SS":
        hours, minutes, seconds = 0, *map(int, timestamp.split(":"))
    else:
        raise ValueError("Invalid time format, must be HH:MM:SS or MM:SS")

    # Normalize seconds and minutes
    total_seconds = hours * 3600 + minutes * 60 + seconds
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours > 0:
        timestamp = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        timestamp = f"00:{minutes:02d}:{seconds:02d}"

    return timestamp


class VideoUnderstandingHighlight(BaseModel):
    start_time: str = Field(description="Start time of the highlight")
    end_time: str = Field(description="End time of the highlight")
    description: Optional[str] = Field(description="Description of the highlight")
    time_format: Literal["HH:MM:SS", "MM:SS"] = Field(
        description="The format of the timestamp"
    )

    @model_validator(mode="after")
    def parse_timestamp(self):
        self.start_time = parse_timestamp_fn(self.start_time, self.time_format)
        self.end_time = parse_timestamp_fn(self.end_time, self.time_format)

        return self


class VideoUnderstandingHighlightsResponse(BaseModel):
    highlights: List[VideoUnderstandingHighlight]


class GeminiVideoUnderstandingService(VideoUnderstandingService):
    def analyze_video_highlights(
        self, video_url: str, prompt: Optional[str] = None
    ) -> HighlightsResponse:

        if not GOOGLE_GENAI_API_KEY:
            raise RuntimeError("GOOGLE_GENAI_API_KEY is not set in environment.")

        client = genai.Client(api_key=GOOGLE_GENAI_API_KEY)

        system_prompt = """
You are a video editor for a YouTube channel who wants to make their content very engaging and interesting, he wants to make short content from his large video.
Please meet the following constraints:

Please meet the following constraints:
- The highlights should be a direct part of the video and should not be out of context
- The highlights should be interesting and clippable, providing value to the viewer
- The highlights should not be too short or too long, but should be just the right length to convey the information
- The highlights should include more than one segment to provide context and continuity
- The highlights should not cut off in the middle of a sentence or idea
- The user provided highlight phrases should be used to generate the highlights
- The highlights should be based on the relevance of the segments to the highlight phrases
- The highlights should be scored out of 100 based on the relevance of the segments to the highlight phrases
- The highlights should start with a catch up phrase and end with a conclusion phrase or with a cliffhanger

Definition of terms:
- Too short highlights: A highlight is considered too short if its duration is less than 5 seconds.
- Too large highlights: A highlight is considered too short if its duration is more than 25 seconds.

Considerations:
- The highlights should be a direct part of the video and should not be out of context
- The response has to be in JSON format, omit other information like code, comments, ``` or ```json.
- The idea has to be complete, no partial ideas allowed.
- All the outcome should be in the same language as the video trasncript.
"""

        contents = types.Content(
            parts=[
                types.Part(file_data=types.FileData(file_uri=video_url)),
                types.Part(text=system_prompt),
            ]
        )

        config: GenerateContentConfigOrDict = {
            "response_mime_type": "application/json",
            "response_schema": VideoUnderstandingHighlightsResponse,
            "media_resolution": MediaResolution.MEDIA_RESOLUTION_LOW,
        }

        response: GenerateContentResponse = client.models.generate_content(
            model=MODEL_NAME, contents=contents, config=config
        )

        if hasattr(response, "parsed"):
            try:
                parsed = response.parsed
                if isinstance(parsed, VideoUnderstandingHighlightsResponse):
                    return self.transform_to_response_highlights(parsed.highlights)
                if isinstance(parsed, dict):
                    return self.transform_to_response_highlights(
                        VideoUnderstandingHighlightsResponse(**parsed).highlights
                    )
            except Exception:
                raise RuntimeError("Error parsing response from Google GenAI.")
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
