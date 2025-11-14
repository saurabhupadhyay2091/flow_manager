from tasks.task1 import run as task1_run
from tasks.task2 import run as task2_run
from tasks.task3 import run as task3_run

TASK_REGISTRY = {
    "task1": task1_run,
    "task2": task2_run,
    "task3": task3_run,
}
