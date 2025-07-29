from typing import List, Any, Optional
from abc import ABC, abstractmethod
from pydantic import BaseModel


# Repository for storing clip URLs associated with highlight IDs


class ClipUrlRepository(ABC):
    @abstractmethod
    def save_clip_urls(self, video_id: str, highlight_to_url: dict[str, str]) -> None:
        """
        Save mapping of highlight IDs to clip URLs for a video.
        """


# Result type for the clip video use case
class ClipResult(BaseModel):
    clips: List[str]
    highlights: Any  # Can be HighlightsResponse or dict, depending on serialization


class Highlight(BaseModel):
    id: str
    start_time: Optional[str]  # e.g. "00:15"
    end_time: Optional[str]  # e.g. "00:45"
    description: Optional[str]


class HighlightsResponse(BaseModel):
    highlights: List[Highlight]


class VideoUnderstandingService(ABC):
    """
    Interface for video understanding services.
    """

    @abstractmethod
    def analyze_video_highlights(
        self, video_url: str, prompt: Optional[str] = None
    ) -> HighlightsResponse:
        pass


class VideoClipperService(ABC):
    @abstractmethod
    def clip_video(self, video_url: str, highlights: "HighlightsResponse") -> list[str]:
        """
        Clip the video based on highlights and return list of clip URLs or paths.
        """


class StorageService(ABC):
    @abstractmethod
    def save_video(self, clip_path: str) -> str:
        """
        Save the video clip to storage and return the storage URL.
        """


class HighlightRepository(ABC):
    @abstractmethod
    def save_highlights(self, video_id: str, highlights: "HighlightsResponse") -> None:
        """
        Save highlights metadata for a video.
        """
