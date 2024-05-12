from recipes.model import ShareModel, method_task_decorator
from app.view import View
from app.pdts import Predictor, PredictorA, PredictorError
from datetime import datetime
class Model(ShareModel):
    def __init__(self, view: View):
        super().__init__(view)
        self.pdts: list[Predictor] = [
            PredictorA()
        ]

    @method_task_decorator
    def run_predictor(self, id: str, ini_date: datetime, days: int,
                      compare_mode: bool, update: bool):
        for pdt in self.pdts:
            if pdt.id == id:
                ini_date_f = ini_date.strftime('%d-%m-%Y')
                ini_date_ts = int(ini_date.timestamp())
                self.view.on_event(f'Running predictor \'{id}\' (ini_date = {ini_date_f} ({ini_date_ts}), days = {days}, compare_mode = {compare_mode} update = {update})')
                try:
                    res = pdt.run(ini_date, days, compare_mode, update)
                    if res is None:
                        self.view.on_success(f'Predictor \'{id}\' has finished: results saved in database')
                    else:
                        self.view.on_success(f'Predictor \'{id}\' has finished: results saved in {res}')
                except PredictorError as e:
                    self.view.on_error(f'Predictor \'{id}\': {e}')
                break
    