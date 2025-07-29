from typing import Any
from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.clipping.tasks import process_clip_video_task
from celery_worker import celery_app

router = APIRouter()


class ClipRequest(BaseModel):
    video_url: str
    prompt: str | None = None


@router.get("/ping")
def ping():
    return {"message": "Clipping service is up"}


@router.post("/clip-async")
def clip_video_async_endpoint(request: ClipRequest) -> dict[str, str]:
    try:
        task = process_clip_video_task.delay(request.video_url, request.prompt)
        return {"task_id": task.id, "status": "processing"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/clip-status/{task_id}")
def get_clip_video_status(task_id: str):
    result: AsyncResult = AsyncResult(task_id, app=celery_app)
    response: dict[str, Any] = {"task_id": task_id, "status": result.status}
    if result.ready():
        response["result"] = result.result
    return response
