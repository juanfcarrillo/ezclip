from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.clipping.router import router as clipping_router
from app.clipping.async_router import router as async_clipping_router
from firebase_init import firebase_app


def create_app() -> FastAPI:
    # Ensure Firebase is initialized
    _ = firebase_app

    python_app = FastAPI(title="ezclip API")

    # Allow CORS from any origin
    python_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add routers
    python_app.include_router(clipping_router, prefix="/clipping", tags=["clipping"])
    python_app.include_router(
        async_clipping_router, prefix="/clipping-async", tags=["clipping-async"]
    )
    # Add middlewares, events, etc. here
    return python_app


app = create_app()
