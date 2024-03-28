from app.view import View
from app.updts import Updater, OutbreaksUpdt, WeatherUpdt, RegionsUpdt, \
    MigrationsUpdt, BirdsUpdt

class Model:
    def __init__(self, view: View) -> None:
        self.updts: list[Updater] = [
            OutbreaksUpdt(),
            WeatherUpdt(),
            RegionsUpdt(),
            MigrationsUpdt(),
            BirdsUpdt()
            # TODO add updaters
        ]

    def update_data(self, ids: list[str]):
        for updt in self.updts:
            if updt.data_id in ids:
                print(f'Running {updt.data_id}')
                updt.run()
                print(f'Finished {updt.data_id}')