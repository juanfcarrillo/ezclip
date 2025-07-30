import os
from typing import List
import ffmpeg  # type: ignore
from app.clipping.domain.video_understanding import (
    VideoClipperService,
    HighlightsResponse,
)
import concurrent.futures


class FFmpegVideoClipper(VideoClipperService):
    """
    Implementation of VideoClipperService using ffmpeg-python for fast and accurate video clipping.
    """

    def clip_video(self, video_url: str, highlights: HighlightsResponse) -> List[str]:
        output_paths: List[str] = []
        base, ext = os.path.splitext(os.path.basename(video_url))

        def to_seconds(ts: str) -> float:
            parts = ts.split(":")
            if len(parts) == 3:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
            elif len(parts) == 2:
                return int(parts[0]) * 60 + float(parts[1])
            else:
                return float(parts[0])

        def process_clip(idx, h):
            if h.start_time is None or h.end_time is None:
                return None
            start = to_seconds(h.start_time)
            end = to_seconds(h.end_time)
            out_path = f"/tmp/{base}_clip{idx}{ext}"
            (
                ffmpeg.input(video_url, ss=start, to=end)
                .output(
                    out_path,
                    c="copy",
                    # vcodec="libx264",
                    # acodec="aac",
                    # movflags="faststart",
                    preset="ultrafast",
                )
                .run(overwrite_output=True)
            )
            return out_path

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(process_clip, idx, h)
                for idx, h in enumerate(highlights.highlights)
            ]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    output_paths.append(result)

        return output_paths
