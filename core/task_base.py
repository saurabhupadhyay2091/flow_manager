from typing import Any, Optional, Dict
from abc import ABC, abstractmethod

class TaskResult(Dict):
    """
    TaskResult protocol:
    {
        "success": bool,
        "data": Optional[Any],  # payload passed to next task(s)
        "meta": Optional[dict]
    }
    """

class BaseTask(ABC):
    name: str

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def run(self, input_data: Optional[dict]) -> TaskResult:
        raise NotImplementedError()
