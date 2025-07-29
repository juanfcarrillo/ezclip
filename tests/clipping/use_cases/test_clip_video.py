from unittest.mock import MagicMock
import typing
import pytest
from app.clipping.use_cases.clip_video import ClipVideoFromHighlightsUseCase
from app.clipping.domain.video_understanding import (
    ClipResult,
    HighlightsResponse,
    Highlight,
)


@pytest.fixture
def mock_services_fixture():
    video_understanding_service = MagicMock()
    video_clipper_service = MagicMock()
    storage_service = MagicMock()
    highlight_repository = MagicMock()
    return (
        video_understanding_service,
        video_clipper_service,
        storage_service,
        highlight_repository,
    )


def test_clip_video_from_highlights_use_case(
    mock_services_fixture: typing.Tuple[MagicMock, MagicMock, MagicMock, MagicMock],
):
    (
        video_understanding_service,
        video_clipper_service,
        storage_service,
        highlight_repository,
    ) = mock_services_fixture
    video_url = "test.mp4"
    prompt = "Find highlights"
    highlights = HighlightsResponse(
        highlights=[
            Highlight(
                start_time="00:00", end_time="00:10", description="Test highlight"
            )
        ]
    )
    clip_paths = ["/tmp/test_clip0.mp4"]
    clip_urls = ["https://storage/test_clip0.mp4"]

    video_understanding_service.analyze_video_highlights.return_value = highlights
    video_clipper_service.clip_video.return_value = clip_paths
    storage_service.save_video.side_effect = lambda path: clip_urls[
        clip_paths.index(path)
    ]

    use_case = ClipVideoFromHighlightsUseCase(
        video_understanding_service,
        video_clipper_service,
        storage_service,
        highlight_repository,
    )

    result = use_case.execute(video_url, prompt)

    video_understanding_service.analyze_video_highlights.assert_called_once_with(
        video_url, prompt
    )
    video_clipper_service.clip_video.assert_called_once_with(video_url, highlights)
    storage_service.save_video.assert_called_once_with(clip_paths[0])
    highlight_repository.save_highlights.assert_called_once_with(video_url, highlights)

    assert isinstance(result, ClipResult)
    assert result.clips == clip_urls
    assert result.highlights == highlights.model_dump()
