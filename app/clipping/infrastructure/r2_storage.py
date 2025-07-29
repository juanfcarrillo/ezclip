import os
from typing import Any
import boto3
from app.clipping.domain.video_understanding import StorageService

from dotenv import load_dotenv
load_dotenv()


class R2StorageService(StorageService):
    """
    Cloudflare R2 implementation for storing video clips.
    Requires boto3: pip install boto3
    """

    def __init__(self):
        self.bucket = os.getenv("R2_BUCKET")
        self.endpoint_url = os.getenv("R2_ENDPOINT_URL")
        self.access_key = os.getenv("R2_ACCESS_KEY_ID")
        self.secret_key = os.getenv("R2_SECRET_ACCESS_KEY")

        self.client: Any = boto3.client(  # type: ignore
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        )

    def save_video(self, clip_path: str) -> str:
        """
        Uploads a video file to R2 and returns the public URL.
        """
        filename = os.path.basename(clip_path)
        try:
            self.client.upload_file(clip_path, self.bucket, filename)
        except Exception as e:
            raise RuntimeError(f"Failed to upload {clip_path} to R2: {e}") from e
        return f"{self.bucket}/{filename}"
