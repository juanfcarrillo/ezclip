from celery import Celery

celery_app: Celery = Celery(
    "ezclip",
    broker="redis://redis-cont:6379/0",
    backend="redis://redis-cont:6379/0",
    include=["app.clipping.tasks"],
)

celery_app.conf.update(
    task_routes={
        "app.clipping.tasks.*": {"queue": "clipping"},
    }
)
