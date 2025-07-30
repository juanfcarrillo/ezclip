import re
from typing import Optional
import logging
from app.clipping.infrastructure.youtube_downloader import download_youtube_video
from app.clipping.domain.video_understanding import (
    VideoUnderstandingService,
    VideoClipperService,
    StorageService,
    HighlightRepository,
    ClipResult,
    ClipUrlRepository,
)


def get_youtube_video_id(url: str) -> str:
    """
    Extracts the YouTube video ID from a given URL.
    Supports both youtube.com and youtu.be formats.
    """

    # Patterns for youtube.com and youtu.be
    patterns = [
        r"(?:v=|\/embed\/|\/v\/|\/shorts\/|youtu\.be\/)([\w-]{11})",
        r"youtube\.com\/watch\?.*v=([\w-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract YouTube video ID from URL: {url}")


class ClipVideoFromHighlightsUseCase:
    def __init__(
        self,
        video_understanding_service: VideoUnderstandingService,
        video_clipper_service: VideoClipperService,
        storage_service: StorageService,
        highlight_repository: HighlightRepository,
        clip_url_repository: ClipUrlRepository,
    ):
        self.video_understanding_service = video_understanding_service
        self.video_clipper_service = video_clipper_service
        self.storage_service = storage_service
        self.highlight_repository = highlight_repository
        self.clip_url_repository = clip_url_repository

    def execute(self, video_url: str, prompt: Optional[str] = None) -> ClipResult:
        logger = logging.getLogger(__name__)
        logger.info("Starting video clipping process for URL: %s", video_url)

        # 1. Analyze video for highlights
        logger.info("Analyzing video for highlights...")
        highlights = self.video_understanding_service.analyze_video_highlights(
            video_url, prompt
        )

        if len(highlights.highlights) == 0:
            raise RuntimeError("No highlights found in the video.")
        logger.info(
            "Highlights found: %s", getattr(highlights, "highlights", highlights)
        )

        # 2. Download YouTube video if needed
        def is_youtube(url: str) -> bool:
            return "youtube.com" in url or "youtu.be" in url

        local_video_path = video_url
        if is_youtube(video_url):
            logger.info("Detected YouTube URL, downloading video...")
            local_video_path = download_youtube_video(video_url)
            logger.info("Downloaded YouTube video to: %s", local_video_path)
        else:
            logger.info("Non-YouTube video, using provided path.")

        # 3. Clip the video based on highlights
        logger.info("Clipping video based on highlights...")
        clip_paths = self.video_clipper_service.clip_video(local_video_path, highlights)
        logger.info("Generated clip paths: %s", clip_paths)

        # 4. Save each clip to storage
        logger.info("Saving clips to storage...")
        clip_urls = [self.storage_service.save_video(path) for path in clip_paths]
        logger.info("Clip URLs: %s", clip_urls)

        video_id = get_youtube_video_id(video_url)

        # 5. Save highlights info (metadata)
        logger.info("Saving highlights metadata...")
        self.highlight_repository.save_highlights(video_id, highlights)

        # 6. Associate highlight ids with clip urls and save
        highlight_to_url: dict[str, str] = {}
        if hasattr(highlights, "highlights") and len(highlights.highlights) == len(
            clip_urls
        ):
            for highlight, url in zip(highlights.highlights, clip_urls):
                highlight_to_url[highlight.id] = url
        logger.info("Saving highlight-to-URL mapping: %s", highlight_to_url)
        self.clip_url_repository.save_clip_urls(video_id, highlight_to_url)

        logger.info("Video clipping process completed.")
        return ClipResult(clips=clip_urls, highlights=highlights.model_dump(), video_id=video_id)
