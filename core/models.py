from typing import List, Optional, Union
from pydantic import BaseModel, Field, validator
from sqlmodel import SQLModel, Field as ORMField, Column, String, Integer, JSON
from datetime import datetime

class TaskModel(BaseModel):
    name: str
    description: Optional[str] = None

class ConditionModel(BaseModel):
    name: str
    description: Optional[str] = None
    source_task: str
    outcome: str = "success"
    # allow single or multiple target tasks (for parallel)
    target_task_success: Union[str, List[str]]
    target_task_failure: Union[str, List[str]] = "end"

    @validator("target_task_success", "target_task_failure", pre=True)
    def normalize_targets(cls, v):
        if isinstance(v, list):
            return v
        return v

class FlowModel(BaseModel):
    id: str
    name: str
    start_task: str
    tasks: List[TaskModel]
    conditions: List[ConditionModel]

class FlowRequest(BaseModel):
    flow: FlowModel


class FlowRun(SQLModel, table=True):
    id: Optional[int] = ORMField(default=None, primary_key=True)
    flow_id: str = ORMField(index=True)
    flow_name: Optional[str] = None
    created_at: datetime = ORMField(default_factory=datetime.utcnow)
    status: str = ORMField(default="running")  # running, completed, failed
    meta: Optional[dict] = ORMField(sa_column=Column(JSON), default=None)

class TaskRun(SQLModel, table=True):
    id: Optional[int] = ORMField(default=None, primary_key=True)
    flow_run_id: int = ORMField(index=True)
    task_name: str
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    status: str = ORMField(default="running")  # running, success, failed
    result: Optional[dict] = ORMField(sa_column=Column(JSON), default=None)
    error: Optional[str] = None
