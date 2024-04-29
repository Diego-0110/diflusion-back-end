from recipes.model import ShareModel, method_task_decorator
from app.view import View
from app.pdts import Predictor, PredictorA
from datetime import datetime
from utils.scripts import noneless_dict
class Model(ShareModel):
    def __init__(self, view: View):
        super().__init__(view)
        self.pdts: list[Predictor] = [
            PredictorA()
        ]

    @method_task_decorator
    def run_predictor(self, id: str, ini_date: datetime = None, days: int = None):
        for pdt in self.pdts:
            if pdt.id == id:
                print('Running')
                kwargs = noneless_dict({
                    'ini_date': ini_date,
                    'days': days
                })
                pdt.run(**kwargs)
                break
    