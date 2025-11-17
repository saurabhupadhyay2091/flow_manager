from core.task_base import BaseTask, TaskResult
from core.registry import register_task
import asyncio

class Task3(BaseTask):
    async def run(self, input_data=None) -> TaskResult:
        await asyncio.sleep(0.1)
        print("[task3] Storing data...")
        # pretend to store (e.g., to some persistent store). Here we just echo back
        print("Stored:", input_data)
        return {"success": True, "data": input_data, "meta": {"stored": True}}

register_task("task3", Task3)
