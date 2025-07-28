from fastapi import FastAPI
from app.clipping.router import router as clipping_router


def create_app() -> FastAPI:
    python_app = FastAPI(title="ezclip API")
    # Add routers
    python_app.include_router(clipping_router, prefix="/clipping", tags=["clipping"])
    # Add middlewares, events, etc. here
    return python_app


app = create_app()
