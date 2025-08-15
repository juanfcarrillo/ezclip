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
        "verbose": False,  # Reduce verbosity to avoid format warnings
        "outtmpl": outtmpl,
        "format": (
            # Try best quality MP4 with height limit first
            "bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/bestaudio[ext=mp4]/"
            # Fallback to any best video+audio combo with height limit
            "bestvideo[height<=1080]+bestaudio[ext=m4a]/bestaudio/"
            # Final fallback to any best single file
            "best[ext=mp4][height<=1080]/"
            "best[height<=1080]/"
            "best"
        ),
        "merge_output_format": "mp4",
        "ignoreerrors": False,
        "no_warnings": True,  # Suppress format selection warnings
        "cookiefile": "cookies.txt",
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)  # type: ignore
        ydl.download(url)  # type: ignore
        return ydl.prepare_filename(info).replace(".webm", ".mp4")  # type: ignore
