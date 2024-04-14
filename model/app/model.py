from app.view import View
from utils.exec import TaskExecutor, task_decorator
from app.pdts import Predictor, PredictorA

class Model:
    task_exec = TaskExecutor()
    def __init__(self, view: View):
        self.pdts: list[Predictor] = [
            PredictorA()
        ]
        self.task_exec.run()

    @task_decorator(task_exec)
    def run_predictor(self, id: str):
        for pdt in self.pdts:
            if pdt.id == id:
                print('Running')
                pdt.run()
    