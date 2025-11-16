# Flow Manager Microservice

## Overview

This is a **Flow Manager** — a microservice that allows you to define and execute a sequence of tasks (a “flow”), with conditions to decide whether to proceed to the next task or terminate, based on each task’s outcome.

In the typical example:

1. **Task 1**: Fetch data  
2. **Task 2**: Process data  
3. **Task 3**: Store data  

The flow definition (in JSON) describes tasks and conditions that guide the control flow. After each task, the flow engine checks whether it succeeded; based on that, it either goes to the next task or stops.

---

## Architecture & Design

### Project Structure


- **main.py**: Runs a FastAPI server.  
- **core/**: Contains the flow execution engine + models.  
- **tasks/**: Each task is implemented in its own module, making it easy to add or modify tasks.

### Flow Execution

1. The client sends a POST request to `/run-flow` with a flow definition (JSON).  
2. The flow definition is parsed into Pydantic models (`FlowModel`, `ConditionModel`, etc.).  
3. A `FlowManager` object is created with the flow config.  
4. `FlowManager.execute()` begins execution at the `start_task`.  
5. For each task:
   - The engine looks up the corresponding function in `TASK_REGISTRY` (in `core/registry.py`).
   - It calls the task function, passing in data from the previous task (if any).
   - It checks the returned result (`{"success": bool, "data": ...}`).
   - Based on `success`, it uses the flow’s conditions to determine the next task.
   - If next task is `"end"`, the flow stops.  
6. The final output (status, final result data) is returned to the client.

---

## Storage / Persistence

### What is currently stored

- **In-memory only**: In the present implementation, **no persistent storage** (database, file, cache) is used.
- Task results (in the form of Python dicts) are stored in local variables while the flow is running:
  - `data_from_prev_task` holds the data passed from one task to the next.
  - The flow manager does **not** write these results to disk or a database.
- After the `execute()` method finishes, all intermediate data is lost, unless explicitly stored by a task.

### Why this design decision

- **Simplicity**: The in-memory approach keeps the engine lightweight and focused purely on control flow logic.
- **Flexibility**: Tasks are free to decide whether or not they want to persist their outputs. For example, a “store data” task can write to database, file, or external service.
- **Decoupling**: The flow manager doesn’t assume *how* storage is done — that’s the responsibility of individual tasks. This keeps the engine generic.

### How to add persistent storage

If you want to persist flow results (or task data) permanently, here are a few strategies:

1. **Database (SQL / NoSQL)**  
   - Use an ORM (e.g. SQLAlchemy) or a driver (e.g. `pymongo`) in tasks to write data to a database.  
   - Example: In `task3.run(...)`, after “storing” data, insert into a DB table/collection.

2. **File System**  
  
3. **In-memory Cache / Key-Value Store**  
   - Use Redis or Memcached to store intermediate or final results.  
   - Tasks can connect to Redis and `SET` / `GET` data as needed.

4. **Event / Message Broker**  
   - Publish task results to a message broker (Kafka, RabbitMQ) for downstream services to consume.  
   - This makes flow manager part of a larger event-driven architecture.

---

## API

- **Endpoint**: `POST /run-flow`  
- **Request Body**:  
  ```json
  {
    "flow": {
      "id": "flow123",
      "name": "Data processing flow",
      "start_task": "task1",
      "tasks": [
        { "name": "task1", "description": "Fetch data" },
        { "name": "task2", "description": "Process data" },
        { "name": "task3", "description": "Store data" }
      ],
      "conditions": [
        {
          "name": "condition_task1",
          "description": "After task1, if success → task2",
          "source_task": "task1",
          "outcome": "success",
          "target_task_success": "task2",
          "target_task_failure": "end"
        },
        {
          "name": "condition_task2",
          "description": "After task2, if success → task3",
          "source_task": "task2",
          "outcome": "success",
          "target_task_success": "task3",
          "target_task_failure": "end"
        }

      ]
    }
  }

 ## **How to Run Locally**

Install dependencies

pip install fastapi uvicorn


**Start the API**

uvicorn main:app --reload


Open the interactive docs
Navigate to: http://127.0.0.1:8000/docs

**Trigger a flow**
Use the /run-flow endpoint in Swagger  UI. Paste your flow JSON and run.
