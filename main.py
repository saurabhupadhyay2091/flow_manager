# main.py
import uvicorn
from fastapi import FastAPI, HTTPException
from core.models import FlowRequest, FlowRun, TaskRun
from core.flow_manager import FlowManager, FlowValidationError
from core.database import init_db, AsyncSessionLocal
from sqlmodel import select
import asyncio

app = FastAPI(title="Flow Manager (async)")

@app.on_event("startup")
async def on_startup():
    # create DB tables
    await init_db()

@app.post("/run-flow")
async def run_flow(req: FlowRequest):
    try:
        manager = FlowManager(req.flow)
    except FlowValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        out = await manager.execute()
        return out
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/flows/{flow_run_id}")
async def get_flow_run(flow_run_id: int):
    async with AsyncSessionLocal() as session:
        q = select(FlowRun).where(FlowRun.id == flow_run_id)
        res = await session.execute(q)
        fr = res.scalar_one_or_none()
        if not fr:
            raise HTTPException(status_code=404, detail="flow run not found")
        # fetch associated tasks
        q2 = select(TaskRun).where(TaskRun.flow_run_id == flow_run_id)
        res2 = await session.execute(q2)
        tasks = res2.scalars().all()
        return {"flow_run": fr, "tasks": tasks}

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=8000)
