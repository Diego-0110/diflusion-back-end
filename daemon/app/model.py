from recipes.model import ShareModel, method_task_decorator
from app.view import View
from app.updts import Updater, UpdaterError, OutbreaksUpdt, WeatherUpdt, RegionsUpdt, MigrationsUpdt, BirdsUpdt

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
            if updt.id in ids:
                self.view.on_event(f'Running updater \'{updt.id}\'')
                try:
                    (in_dups, m_dups, w_dups) = updt.run()
                except UpdaterError as e:
                    self.view.on_error(f'Updater \'{updt.id}\': {e}')
                self.view.on_success(f'Updater \'{updt.id}\' has finished. Duplicates: {in_dups} from input, {m_dups} in model db, {w_dups} in web db')
    # TODO other operations