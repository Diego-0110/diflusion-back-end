from recipes.view import ShareView
from utils.exec import TaskExecutor

def method_task_decorator(func):
    def wrapper(*arg, **kwargs):
        def task():
            func(*arg, **kwargs)
        arg[0].task_exec.add_task(task)
    return wrapper

class ShareModel:
    def __init__(self, view: ShareView):
        self.view = view
        self.task_exec = TaskExecutor()
        self.task_exec.run()
    
    def stop(self):
        self.task_exec.stop()