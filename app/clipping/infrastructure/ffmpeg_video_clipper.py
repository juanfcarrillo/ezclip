import os
from typing import List
import concurrent.futures
import ffmpeg  # type: ignore
from app.clipping.domain.video_understanding import (
    VideoClipperService,
    HighlightsResponse,
)


class FFmpegVideoClipper(VideoClipperService):
    """
    Implementation of VideoClipperService using ffmpeg-python for fast and accurate video clipping.
    """

    def clip_video(self, video_url: str, highlights: HighlightsResponse) -> List[str]:
        output_paths: List[str] = []
        base, ext = os.path.splitext(os.path.basename(video_url))

        def to_seconds(ts: str) -> float:
            parts = ts.split(":")
            if len(parts) != 3:
                raise ValueError(f"Timestamp '{ts}' is not in HH:MM:SS format.")
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])

        def process_clip(idx, h):
            if h.start_time is None or h.end_time is None:
                return None
            start = to_seconds(h.start_time)
            end = to_seconds(h.end_time)
            out_path = f"/tmp/{base}_clip{idx}{ext}"
            try:
                (
                    ffmpeg.input(video_url, ss=start, to=end + 10)
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
            except ffmpeg.Error as e:
                print(f"Error processing clip {idx}: {e}")
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
