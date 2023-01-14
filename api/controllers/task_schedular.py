
from fastapi import APIRouter, HTTPException, Body

from api.validators.task_schedular import TaskSchedulerValidator
from main import celery

# APIRouter creates path operations for product module
router = APIRouter(
    prefix="",
    tags=["dataHandler"],
    responses={404: {"description": "Not found"}},
)


@router.post("/add/celery-task", response_description="")
async def add_refresh_task(data: TaskSchedulerValidator):
    """"""
    from api.service.celery_service import task_scheduler

    await task_scheduler(data)
    return True


@router.get("revoke/task", response_description="revoke-task")
async def save_symbol_price_ticker(task_id: str):
    try:
        celery.control.revoke(task_id)
        return True
    except Exception as e:
        return e


