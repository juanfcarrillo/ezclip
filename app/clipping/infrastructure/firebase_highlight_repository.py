from firebase_admin.firestore import client
from app.clipping.domain.video_understanding import (
    HighlightRepository,
    HighlightsResponse,
)
from firebase_init import firebase_app


class FirebaseHighlightRepository(HighlightRepository):
    """
    Firestore implementation for storing video highlights metadata.
    Requires firebase_admin to be initialized.
    """

    def __init__(self):
        self.db = client(firebase_app)

    def save_highlights(self, video_id: str, highlights: HighlightsResponse) -> None:
        # Encode video_id to ensure it's a valid Firestore document ID
        doc_ref = self.db.collection("video_highlights").document(video_id)
        doc_ref.set({"highlights": highlights.model_dump()})
