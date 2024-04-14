import threading
import types

class TaskExecutor:
    def __init__(self) -> None:
        self.tasks: list[types.FunctionType] = []
        self.tasks_lck = threading.Lock()
        self.is_running = True

    def add_task(self, task: types.FunctionType):
        self.tasks_lck.acquire()
        self.tasks.append(task)
        self.tasks_lck.release()

    def exec_loop(self):
        while self.is_running:
            self.tasks_lck.acquire()
            if self.tasks:
                self.tasks_lck.release()
                task = self.tasks[0]
                task()
                self.tasks_lck.acquire()
                self.tasks = self.tasks[1:]
            self.tasks_lck.release()

    def run(self):
        th = threading.Thread(target=self.exec_loop)
        th.start()
    
    def stop(self):
        self.is_running = False

def task_decorator(task_exec: TaskExecutor):
    def decorator(func):
        def wrapper(*arg, **kwargs):
            def task():
                func(*arg, **kwargs)
            task_exec.add_task(task)
        return wrapper
    return decorator