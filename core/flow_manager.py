from core.registry import TASK_REGISTRY
from core.models import FlowModel


class FlowManager:

    def __init__(self, flow_config: FlowModel):
        self.flow = flow_config
        self.conditions = {c.source_task: c for c in flow_config.conditions}

    def execute(self):
        current_task_name = self.flow.start_task
        data_from_prev = None

        while current_task_name != "end":
            print(f"\n--- Executing: {current_task_name} ---")

            task_fn = TASK_REGISTRY.get(current_task_name)
            if not task_fn:
                raise ValueError(f"Task {current_task_name} is not defined.")

            result = task_fn(data_from_prev)
            print(f"Result: {result}")

            condition = self.conditions.get(current_task_name)
            if not condition:
                print("No condition found — ending flow.")
                return {"status": "completed", "result": result}

            if result.get("success"):
                next_task = condition.target_task_success
            else:
                next_task = condition.target_task_failure

            if next_task == "end":
                print("Flow ended.")
                return {"status": "ended", "final_task": current_task_name, "result": result}

            data_from_prev = result.get("data")
            current_task_name = next_task
