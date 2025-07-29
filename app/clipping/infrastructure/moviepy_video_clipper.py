import os
from typing import List
from moviepy import VideoFileClip
from app.clipping.domain.video_understanding import (
    VideoClipperService,
    HighlightsResponse,
)


class MoviePyVideoClipper(VideoClipperService):
    """
    Implementation of VideoClipperService using moviepy 2.2.1+ to clip videos based on highlights.
    """

    def clip_video(self, video_url: str, highlights: HighlightsResponse) -> List[str]:
        output_paths: List[str] = []
        base, ext = os.path.splitext(os.path.basename(video_url))
        video = VideoFileClip(video_url)

        def to_seconds(ts: str) -> int:
            parts = ts.split(":")
            return int(parts[0]) * 60 + int(parts[1])

        for idx, h in enumerate(highlights.highlights):
            if h.start_time is None or h.end_time is None:
                continue
            start = to_seconds(h.start_time)
            end = to_seconds(h.end_time)
            clip = video.subclipped(start, end)
            out_path = f"/tmp/{base}_clip{idx}{ext}"
            clip.write_videofile(out_path, codec="libx264", audio_codec="aac", logger=None)
            output_paths.append(out_path)

        video.close()
        return output_paths
