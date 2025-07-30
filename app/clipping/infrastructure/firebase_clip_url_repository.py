from firebase_admin.firestore import client
from app.clipping.domain.video_understanding import ClipUrlRepository
from firebase_init import firebase_app


class FirebaseClipUrlRepository(ClipUrlRepository):
    """
    Firestore implementation for storing highlight ID to clip URL mappings.
    Requires firebase_admin to be initialized.
    """

    def __init__(self):
        self.db = client(firebase_app)

    def save_clip_urls(self, video_id: str, highlight_to_url: dict[str, str]) -> None:
        doc_ref = self.db.collection("video_clip_urls").document(video_id)
        doc_ref.set({"highlight_to_url": highlight_to_url})
