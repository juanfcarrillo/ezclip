from fastapi import APIRouter, HTTPException
import os
from pydantic import BaseModel
from app.clipping.use_cases.clip_video import ClipVideoFromHighlightsUseCase
from app.clipping.infrastructure.r2_storage import R2StorageService
from app.clipping.infrastructure.firebase_highlight_repository import (
    FirebaseHighlightRepository,
)
from app.clipping.infrastructure.gemini_video_understanding import (
    GeminiVideoUnderstandingService,
)
from app.clipping.infrastructure.moviepy_video_clipper import MoviePyVideoClipper
from app.clipping.domain.video_understanding import ClipResult
from app.clipping.infrastructure.firebase_clip_url_repository import (
    FirebaseClipUrlRepository,
)
import boto3

router = APIRouter()


class ClipRequest(BaseModel):
    video_url: str
    prompt: str | None = None


use_case = ClipVideoFromHighlightsUseCase(
    video_understanding_service=GeminiVideoUnderstandingService(),
    video_clipper_service=MoviePyVideoClipper(),
    storage_service=R2StorageService(),
    highlight_repository=FirebaseHighlightRepository(),
    clip_url_repository=FirebaseClipUrlRepository(),
)


class VideoUrlRequest(BaseModel):
    filename: str


@router.post("/video-url")
def get_video_url(request: VideoUrlRequest):
    filename = request.filename.split("/")[-1]
    url = f"https://pub-384e2f668fd549bd8db6899b615291ce.r2.dev/{filename}"
    return {"url": url}


@router.get("/ping")
def ping():
    return {"message": "Clipping service is up"}


@router.post("/clip", response_model=ClipResult)
def clip_video_endpoint(request: ClipRequest):
    try:
        result = use_case.execute(request.video_url, request.prompt)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
