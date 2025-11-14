from fastapi import FastAPI
from core.models import FlowRequest
from core.flow_manager import FlowManager

app = FastAPI(title="Flow Manager Microservice")


@app.post("/run-flow")
def run_flow(req: FlowRequest):
    manager = FlowManager(req.flow)
    result = manager.execute()
    return {"flow_id": req.flow.id, "output": result}
