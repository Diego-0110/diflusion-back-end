from recipes.model import ShareModel, method_task_decorator
from app.view import View
from app.fmts import Formatter, FormatterError, OutbreaksFmt, WeatherFmt, RegionsFmt, MigrationsFmt, BirdsFmt

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
                self.view.on_event(f'Running formatter \'{fmt.data_id}\'')
                try:
                    (total, invalid) = fmt.run()
                except FormatterError as e:
                    self.view.on_error(f'Formatter \'{fmt.data_id}\': {e}')
                    break
                self.view.on_success(f'Formatter \'{fmt.data_id}\' has finished: {total} valid entries, {invalid} invalid entries')
