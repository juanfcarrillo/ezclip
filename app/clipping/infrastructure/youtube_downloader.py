import os
import tempfile
from typing import Any
from yt_dlp import YoutubeDL  # type: ignore


def download_youtube_video(url: str) -> str:
    download_dir = tempfile.gettempdir()
    outtmpl = os.path.join(download_dir, "%(id)s.%(ext)s")
    ydl_opts: dict[str, Any] = {
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Sec-Fetch-Mode": "navigate",
        },
        "geo_bypass": True,
        "verbose": True,
        "outtmpl": outtmpl,
        "format": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best[height<=1080]",
        "merge_output_format": "mp4",
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)  # type: ignore
        ydl.download(url)  # type: ignore
        return ydl.prepare_filename(info).replace(".webm", ".mp4")  # type: ignore
