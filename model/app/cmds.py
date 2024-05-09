from app.model import Model
from utils.cmd import Command, RunCmdError
from datetime import datetime
class RunPredictorCmd(Command):
    def __init__(self, model: Model):
        super().__init__('predict', 'run a preditor starting from a certain date and for DAYS days')
        self.model = model
        self.parser.add_argument('id', choices=[pdt.id for pdt in self.model.pdts])
        self.parser.add_argument('-date', default=None, type=str)
        self.parser.add_argument('-days', default=7, type=int) # TODO const
        self.parser.add_argument('--compare-mode', default=False,
                                 action='store_true', dest='c_mode')
        self.parser.add_argument('--update', default=False,
                                 action='store_true', dest='update')
    
    def run(self, args):
        date = datetime.now()
        date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        if args.date is not None:
            try:
                date = datetime.strptime(args.date, '%d-%m-%Y')
            except ValueError:
                raise RunCmdError('-date should have the format dd-mm-YYYY')
        self.model.run_predictor(args.id, date, args.days, args.c_mode, args.update)
        return f'Predictor \'{args.id}\' will be executed...'
