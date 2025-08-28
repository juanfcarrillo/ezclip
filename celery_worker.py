import os
from celery import Celery

# Use different Redis URLs for local vs Docker environments
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app: Celery = Celery(
    "ezclip",
    broker=redis_url,
    backend=redis_url,
    include=["app.clipping.tasks"],
)

celery_app.conf.update(
    task_routes={
        "app.clipping.tasks.*": {"queue": "clipping"},
    }
)
