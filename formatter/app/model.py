from recipes.model import ShareModel, method_task_decorator
from app.view import View
from app.fmts import Formatter, OutbreaksFmt, WeatherFmt, RegionsFmt, MigrationsFmt, BirdsFmt

class Model(ShareModel):
    def __init__(self, view: View):
        super().__init__(view)
        self.fmts: list[Formatter] = [
            OutbreaksFmt(),
            WeatherFmt(),
            RegionsFmt(),
            MigrationsFmt(),
            BirdsFmt()
        ]

    @method_task_decorator
    def format_data(self, ids: list[str]):
        for fmt in self.fmts:
            if fmt.data_id in ids:
                print(f'Running {fmt.data_id}')
                fmt.run()
                print(f'Finished {fmt.data_id}')
