import threading
import types
from datetime import datetime, timedelta
import bisect
import math
class TaskExecutor:
    # Executes task from a task list creating a thread for the executor
    # Thread safe and
    # With an event to avoid bad performance when there's no task
    def __init__(self) -> None:
        self.tasks: list[types.FunctionType] = []
        self.tasks_lck = threading.Lock()
        self.tasks_evt = threading.Event()
        self.is_running = True

    def add_task(self, task: types.FunctionType):
        self.tasks_lck.acquire()
        self.tasks.append(task)
        self.tasks_evt.set()
        self.tasks_lck.release()

    def exec_loop(self):
        while self.is_running:
            self.tasks_lck.acquire()
            if self.tasks:
                task = self.tasks[0]
                self.tasks_lck.release()
                task()
                self.tasks_lck.acquire()
                self.tasks = self.tasks[1:]
                if not self.tasks:
                    self.tasks_evt.clear()
            self.tasks_lck.release()
            self.tasks_evt.wait() # Wait until len(task) > 0 or stop is called

    def run(self):
        th = threading.Thread(target=self.exec_loop)
        th.start()
    
    def stop(self):
        # Stop the executor safely:
        # if a task is being executed, it lets the taks end
        self.is_running = False
        self.tasks_evt.set()

# Decorator to add a function as a task when is called
def task_decorator(task_exec: TaskExecutor):
    def decorator(func):
        def wrapper(*arg, **kwargs):
            def task():
                func(*arg, **kwargs)
            task_exec.add_task(task)
        return wrapper
    return decorator

class CronTask:
    def __init__(self, task: types.FunctionType, exec_time: datetime,
                 time_delta: timedelta = None):
        self.task = task
        self.exec_time = exec_time
        self.time_delta = time_delta
    
    def __lt__(self, other):
        if not isinstance(other, CronTask):
            raise TypeError('Invalid type comparison')
        return self.exec_time < other.exec_time
    
    def __gt__(self, other):
        if not isinstance(other, CronTask):
            raise TypeError('Invalid type comparison')
        return self.exec_time > other.exec_time

class CronTaskExecutor:
    # Similar to TaskExecutor but the tasks have an execution time and an
    # option to repeat the task every x time
    def __init__(self):
        self.tasks: list[CronTask] = []
        self.tasks_lck = threading.Lock()
        self.tasks_evt = threading.Event()
        self.urgent_task_evt = threading.Event()
        self.is_running = True
    
    def add_task(self, cron_task: CronTask):
        self.tasks_lck.acquire()
        bisect.insort(self.tasks, cron_task)
        if self.tasks.index(cron_task) == 0:
            # cron_task is a new more urget task
            self.urgent_task_evt.set()
        self.tasks_evt.set()
        self.tasks_lck.release()
    
    def clear_tasks(self):
        self.tasks_lck.acquire()
        self.tasks = []
        self.urgent_task_evt.set()
        self.tasks_evt.clear()
        self.tasks_lck.release()
    
    def exec_loop(self):
        while self.is_running:
            self.tasks_lck.acquire()
            if self.tasks:
                cron_task = self.tasks[0]
                self.tasks_lck.release()
                timestamp_now = datetime.now().timestamp()
                time_diff = cron_task.exec_time.timestamp() - timestamp_now
                time_diff = math.ceil(time_diff)
                if time_diff <= 0:
                    cron_task.task()
                    self.tasks_lck.acquire()
                    del self.tasks[self.tasks.index(cron_task)]
                    if isinstance(cron_task.time_delta, timedelta):
                        self.tasks_lck.release()
                        cron_task.exec_time += cron_task.time_delta
                        self.add_task(cron_task)
                    else:
                        if not self.tasks:
                            self.tasks_evt.clear()
                        self.tasks_lck.release()
                else:
                    self.urgent_task_evt.wait(timeout=time_diff)
                    self.urgent_task_evt.clear()
            else:
                self.tasks_lck.release()
            self.tasks_evt.wait() # Wait until len(task) > 0 or stop is called

    def run(self):
        th = threading.Thread(target=self.exec_loop)
        th.start()

    def stop(self):
        # Stop the executor safely:
        # if a task is being executed, it lets the taks end
        self.is_running = False
        self.tasks_evt.set()
        self.urgent_task_evt.set()