
# Flow Manager Microservice

This project implements a **Flow Manager Microservice** that executes a sequence of tasks based on a JSON-defined workflow.  
Each task produces a success/failure result, and based on conditions, the flow manager decides whether to continue to the next task or end the flow.

The system is built using **FastAPI**, supports **async task execution**, and stores each flow run & task run in a local SQLite database using **SQLModel**.

---

##  Key Features

- **JSON-driven flow definition** (tasks, conditions, start task)
- **Async task execution**
- **Sequential or parallel task execution**
- **Task registry system** allowing easy plug-and-play of new tasks
- **Full database logging** (success, failure, timestamps, outputs)
- **Flow validation** (invalid tasks/conditions detected early)

---

##  Approach

The microservice is designed around the concept of a **flow**, which consists of:

- A list of **tasks**
- A set of **conditions**
- A **start task**

Each task implements an async `run()` method and returns:

```json
{
  "success": true | false,
  "data": { ... }
}

```

# Enhancements Implemented in the Flow Manager Microservice

This project includes several advanced enhancements beyond basic sequential task execution.

---

##  1. Task Classes + Interfaces

All tasks inherit from a common `BaseTask` interface:

- Ensures consistency across tasks  
- Forces implementation of an async `run()` method  
- Enhances modularity and reusability  
- Allows dynamic task registration using a registry pattern

This design makes it easy to plug new tasks into the system without modifying core code.

---

##  2. Full Error Handling & Validation

Several validations and protections are added:

### **Flow Validation**
- Ensures that the `start_task` exists  
- Ensures all tasks used in conditions exist  
- Ensures target tasks point to valid tasks or `"end"`  

### **Runtime Error Handling**
If any task raises an exception:
- TaskRun is marked as **failed**
- The full traceback is stored in the database
- FlowRun is marked as **failed**
- The error is returned to the API caller

This provides strong reliability guarantees and makes debugging easier.

---

##  3. Database Persistence (SQLModel)

The following are stored:

### **FlowRun (1 per flow execution)**
- Flow ID + metadata  
- Status (`running`, `completed`, `failed`)  
- Logs and errors  

### **TaskRun (1 per executed task)**
- Start time / end time  
- Success/failure status  
- Returned data  
- Error message or traceback  

This system provides:
- Full audit history  
- Observability  
- Ability to reconstruct flow execution paths

---

##  4. Async Task Execution

All tasks are executed using `asyncio` and support:
- Awaitable I/O operations  
- High throughput  
- Non-blocking execution  

Tasks use:
```python
async def run(...)

```
# FastAPI Microservice Endpoints

This microservice exposes two main API endpoints for running flows and retrieving past execution results.

---

## **POST /run-flow**

Runs a flow based on the JSON definition provided in the request body.

### **Description**
- Accepts a full flow configuration (tasks, conditions, start task)
- Executes tasks sequentially or in parallel based on conditions
- Returns execution logs, status, and flow_run_id

## **GET /flows/{id}**

Fetches the full execution details of a previously executed flow.

---

### **Description**

This endpoint retrieves all stored information about a flow execution, including:

- **Saved metadata** from the database  
- **Flow-level status** (running, completed, failed)  
- **Task-level execution logs**  
- **Success/failure status** for each task  
- **Timestamps** (started_at, finished_at)  
- **Task outputs** returned by each task  
- **Errors and full tracebacks**, if any task failed  

This makes it possible to debug flows, audit execution history, and visualize the execution path.

---


