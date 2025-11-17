from core.task_base import BaseTask, TaskResult
from core.registry import register_task
import asyncio

class Task1(BaseTask):
    async def run(self, input_data=None) -> TaskResult:
        # simulate IO
        await asyncio.sleep(0.1)
        print("[task1] Fetching data...")
        data = {"value": 10}
        return {"success": True, "data": data, "meta": {"info": "fetched 10"}}

# register
register_task("task1", Task1)
