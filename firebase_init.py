import os
from firebase_admin import initialize_app
import firebase_admin.credentials as credentials
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH")
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")


def initialize_firebase_app():
    cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)

    app = initialize_app(cred, {
        'projectId': FIREBASE_PROJECT_ID
    })

    return app


firebase_app = initialize_firebase_app()
