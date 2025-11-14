from pydantic import BaseModel
from typing import List

class TaskModel(BaseModel):
    name: str
    description: str

class ConditionModel(BaseModel):
    name: str
    description: str
    source_task: str
    outcome: str
    target_task_success: str
    target_task_failure: str

class FlowModel(BaseModel):
    id: str
    name: str
    start_task: str
    tasks: List[TaskModel]
    conditions: List[ConditionModel]

class FlowRequest(BaseModel):
    flow: FlowModel
