from recipes.model import ShareModel, method_task_decorator
from app.view import View
from app.updts import Updater, OutbreaksUpdt, WeatherUpdt, RegionsUpdt, \
    MigrationsUpdt, BirdsUpdt

class Model(ShareModel):
    def __init__(self, view: View):
        super().__init__(view)
        self.updts: list[Updater] = [
            OutbreaksUpdt(),
            WeatherUpdt(),
            RegionsUpdt(),
            MigrationsUpdt(),
            BirdsUpdt()
        ]
    
    @method_task_decorator
    def update_data(self, ids: list[str]):
        for updt in self.updts:
            if updt.data_id in ids:
                print(f'Running {updt.data_id}')
                updt.run()
                print(f'Finished {updt.data_id}')
    # TODO other operations