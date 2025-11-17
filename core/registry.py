from typing import Dict
from core.task_base import BaseTask


TASK_REGISTRY: Dict[str, type] = {}

def register_task(name: str, task_cls: type):
    if not issubclass(task_cls, BaseTask):
        raise ValueError("task_cls must subclass BaseTask")
    TASK_REGISTRY[name] = task_cls

def get_task_cls(name: str):
    return TASK_REGISTRY.get(name)
