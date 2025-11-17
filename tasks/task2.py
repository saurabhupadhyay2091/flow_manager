from core.task_base import BaseTask, TaskResult
from core.registry import register_task
import asyncio

class Task2(BaseTask):
    async def run(self, input_data=None) -> TaskResult:
        await asyncio.sleep(0.2)
        print("[task2] Processing data...")
        if not input_data or "value" not in input_data:
            return {"success": False, "data": None, "meta": {"reason": "missing value"}}
        processed = input_data["value"] * 2
        return {"success": True, "data": {"processed": processed}, "meta": {"processed_from": input_data}}

register_task("task2", Task2)
