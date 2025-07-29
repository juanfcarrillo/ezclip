from typing import Optional
from app.clipping.infrastructure.youtube_downloader import download_youtube_video
from app.clipping.domain.video_understanding import (
    VideoUnderstandingService,
    VideoClipperService,
    StorageService,
    HighlightRepository,
    ClipResult,
    ClipUrlRepository,
)


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
        # 1. Analyze video for highlights
        highlights = self.video_understanding_service.analyze_video_highlights(
            video_url, prompt
        )

        # 2. Download YouTube video if needed
        def is_youtube(url: str) -> bool:
            return "youtube.com" in url or "youtu.be" in url

        local_video_path = video_url
        if is_youtube(video_url):
            local_video_path = download_youtube_video(video_url)

        # 3. Clip the video based on highlights
        clip_paths = self.video_clipper_service.clip_video(local_video_path, highlights)

        # 4. Save each clip to storage
        clip_urls = [self.storage_service.save_video(path) for path in clip_paths]

        # 5. Save highlights info (metadata)
        self.highlight_repository.save_highlights(video_url, highlights)

        # 6. Associate highlight ids with clip urls and save
        highlight_to_url: dict[str, str] = {}
        if hasattr(highlights, "highlights") and len(highlights.highlights) == len(
            clip_urls
        ):
            for highlight, url in zip(highlights.highlights, clip_urls):
                highlight_to_url[highlight.id] = url
        self.clip_url_repository.save_clip_urls(video_url, highlight_to_url)

        return ClipResult(clips=clip_urls, highlights=highlights.model_dump())
