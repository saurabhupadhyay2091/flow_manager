import asyncio
from typing import Any, Dict, List, Optional, Union
from core.models import FlowModel, TaskRun, FlowRun
from core.registry import get_task_cls
from core.database import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
import traceback
import json

class FlowValidationError(Exception):
    pass

class FlowManager:
    def __init__(self, flow_config: FlowModel):
        self.flow = flow_config
        # map conditions by source_task name
        self.conditions = {c.source_task: c for c in flow_config.conditions}
        self.task_names = {t.name for t in flow_config.tasks}
        self._validate_flow()

    def _validate_flow(self):
        # start task must be present
        if self.flow.start_task not in self.task_names:
            raise FlowValidationError(f"start_task '{self.flow.start_task}' is not in tasks")

        for cond in self.flow.conditions:
            if cond.source_task not in self.task_names:
                raise FlowValidationError(f"condition source_task '{cond.source_task}' unknown")
            def check_target(target):
                if target == "end":
                    return True
                if isinstance(target, list):
                    return all(t in self.task_names for t in target)
                return target in self.task_names
            if not check_target(cond.target_task_success):
                raise FlowValidationError(f"Invalid success target in condition {cond.name}")
            if not check_target(cond.target_task_failure):
                raise FlowValidationError(f"Invalid failure target in condition {cond.name}")

    async def _persist_flow_run(self, flow_run: FlowRun):
        async with AsyncSessionLocal() as session:
            session.add(flow_run)
            await session.commit()
            await session.refresh(flow_run)
            return flow_run

    async def _persist_task_run(self, task_run: TaskRun):
        async with AsyncSessionLocal() as session:
            session.add(task_run)
            await session.commit()
            await session.refresh(task_run)
            return task_run

    async def _update_task_run(self, task_run_id: int, **kwargs):
        async with AsyncSessionLocal() as session:
            q = select(TaskRun).where(TaskRun.id == task_run_id)
            res = await session.execute(q)
            tr = res.scalar_one_or_none()
            if not tr:
                return None
            for k, v in kwargs.items():
                setattr(tr, k, v)
            await session.commit()
            await session.refresh(tr)
            return tr

    async def execute(self) -> Dict[str, Any]:
        flow_run = FlowRun(flow_id=self.flow.id, flow_name=self.flow.name, status="running", meta={"flow": self.flow.dict()})
        flow_run = await self._persist_flow_run(flow_run)
        execution_log = []
        current_tasks: List[str] = [self.flow.start_task]
        data_store: Dict[str, Any] = {}  # store last data per task

        try:
            while current_tasks:

                coros = []
                for task_name in current_tasks:
                    task_cls = get_task_cls(task_name)
                    if not task_cls:
                        raise FlowValidationError(f"Task '{task_name}' not registered")
                    # instantiate task
                    task_instance = task_cls(task_name)
                    input_data = data_store.get(task_name) or data_store.get("_prev")  # allow some flexibility
                    coros.append(self._run_task_wrapper(task_instance, input_data, flow_run.id))

                results = await asyncio.gather(*coros, return_exceptions=True)

                next_tasks: List[str] = []
                outputs_by_task = {}

                for res in results:
                    if isinstance(res, Exception):
                        raise res
                    execution_log.append(res)
                    outputs_by_task[res["task_name"]] = res
                    cond = self.conditions.get(res["task_name"])
                    if not cond:
                        continue
                    # check outcome (we compare with cond.outcome; currently flow supports only success/failure)
                    success_flag = bool(res.get("success"))
                    targets = cond.target_task_success if success_flag else cond.target_task_failure
                    if isinstance(targets, list):
                        targets_list = targets
                    else:
                        targets_list = [targets]
                    for t in targets_list:
                        if t == "end":
                            continue
                        if t not in next_tasks:
                            next_tasks.append(t)
                            data_store[t] = res.get("data")

                current_tasks = next_tasks

            async with AsyncSessionLocal() as session:
                q = select(FlowRun).where(FlowRun.id == flow_run.id)
                res = await session.execute(q)
                fr = res.scalar_one()
                fr.status = "completed"
                fr.meta = {"execution_log": execution_log}
                await session.commit()

            return {"status": "completed", "flow_run_id": flow_run.id, "execution_log": execution_log}

        except Exception as exc:
            # mark flow run failed
            async with AsyncSessionLocal() as session:
                q = select(FlowRun).where(FlowRun.id == flow_run.id)
                res = await session.execute(q)
                fr = res.scalar_one()
                fr.status = "failed"
                fr.meta = {"error": str(exc), "traceback": traceback.format_exc()}
                await session.commit()
            raise

    async def _run_task_wrapper(self, task_instance, input_data, flow_run_id: int) -> Dict:
        task_run = TaskRun(flow_run_id=flow_run_id, task_name=task_instance.name, started_at=None, status="running")
        task_run = await self._persist_task_run(task_run)
        task_run_id = task_run.id

        import datetime
        start = datetime.datetime.utcnow()
        await self._update_task_run(task_run_id, started_at=start, status="running")

        try:
            result = await task_instance.run(input_data)
            end = datetime.datetime.utcnow()
            success_flag = bool(result.get("success"))
            await self._update_task_run(
                task_run_id,
                finished_at=end,
                status="success" if success_flag else "failed",
                result=result,
            )
            return {
                "task_run_id": task_run_id,
                "task_name": task_instance.name,
                "success": success_flag,
                "data": result.get("data"),
                "result": result,
                "error": None,
            }
        except Exception as exc:
            end = datetime.datetime.utcnow()
            tb = traceback.format_exc()
            await self._update_task_run(
                task_run_id,
                finished_at=end,
                status="failed",
                error=str(exc),
                result={"exception": str(exc), "traceback": tb},
            )
            raise
