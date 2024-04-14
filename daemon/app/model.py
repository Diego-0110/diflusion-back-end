from app.view import View
from utils.exec import TaskExecutor, task_decorator
from app.updts import Updater, OutbreaksUpdt, WeatherUpdt, RegionsUpdt, \
    MigrationsUpdt, BirdsUpdt

class Model:
    task_exec = TaskExecutor()
    def __init__(self, view: View) -> None:
        self.updts: list[Updater] = [
            OutbreaksUpdt(),
            WeatherUpdt(),
            RegionsUpdt(),
            MigrationsUpdt(),
            BirdsUpdt()
            # TODO add updaters
        ]
        self.task_exec.run()

    @task_decorator(task_exec)
    def update_data(self, ids: list[str]):
        for updt in self.updts:
            if updt.data_id in ids:
                print(f'Running {updt.data_id}')
                updt.run()
                print(f'Finished {updt.data_id}')
    # TODO other operations