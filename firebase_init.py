import os
from firebase_admin import initialize_app
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
firebase_app = initialize_app(cred, {"projectId": FIREBASE_PROJECT_ID})
