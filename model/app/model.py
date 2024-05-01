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
                      compare_mode: bool):
        for pdt in self.pdts:
            if pdt.id == id:
                self.view.on_event(f'Running predictor \'{id}\'')
                try:
                    res = pdt.run(ini_date, days, compare_mode)
                except PredictorError as e:
                    self.view.on_error(f'Predictor \'{id}\': {e}')
                if res is None:
                    self.view.on_success(f'Predictor \'{id}\' has finished: results saved in database')
                else:
                    self.view.on_success(f'Predictor \'{id}\' has finished: results saved in {res}')
                break
    