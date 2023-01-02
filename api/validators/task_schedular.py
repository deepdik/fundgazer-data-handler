from pydantic.main import BaseModel

from api.models.general_models import DataRefreshType, TaskDueType


class TaskSchedulerValidator(BaseModel):
    refresh_type: DataRefreshType
    run_after: TaskDueType
    run_after_val: int
    data: dict

