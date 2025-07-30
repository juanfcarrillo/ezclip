from celery_worker import celery_app
from app.clipping.use_cases.clip_video import ClipVideoFromHighlightsUseCase

from app.clipping.infrastructure.r2_storage import R2StorageService
from app.clipping.infrastructure.firebase_highlight_repository import (
    FirebaseHighlightRepository,
)
from app.clipping.infrastructure.gemini_video_understanding import (
    GeminiVideoUnderstandingService,
)
from app.clipping.infrastructure.firebase_clip_url_repository import (
    FirebaseClipUrlRepository,
)
from app.clipping.infrastructure.ffmpeg_video_clipper import FFmpegVideoClipper

use_case = ClipVideoFromHighlightsUseCase(
    video_understanding_service=GeminiVideoUnderstandingService(),
    video_clipper_service=FFmpegVideoClipper(),
    storage_service=R2StorageService(),
    highlight_repository=FirebaseHighlightRepository(),
    clip_url_repository=FirebaseClipUrlRepository(),
)


@celery_app.task
def process_clip_video_task(video_url: str, prompt: str | None = None):
    result = use_case.execute(video_url, prompt)
    return result.model_dump()
