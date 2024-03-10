from app.view import View
from app.fmts import Formatter, OutbreaksFmt, MigrationsFmt, BirdsFmt
class Model:
    def __init__(self, view: View) -> None:
        self.fmts: list[Formatter] = [
            OutbreaksFmt(),
            MigrationsFmt(),
            BirdsFmt()
        ]

    def upload_file(self):
        pass

    def format_data(self, ids: list[str]):
        for fmt in self.fmts:
            if fmt.data_id in ids:
                print(f'Running {fmt.data_id}')
                fmt.run()
                print(f'Finished {fmt.data_id}')

    def show_data_status(self):
        pass