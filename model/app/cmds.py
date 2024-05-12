from app.model import Model
from utils.cmd import Command, RunCmdError
from datetime import datetime
class RunPredictorCmd(Command):
    def __init__(self, model: Model):
        super().__init__('predict', 'run a preditor starting from a certain date and for DAYS days')
        self.model = model
        self.parser.add_argument('id', choices=[pdt.id for pdt in self.model.pdts])
        self.parser.add_argument('-date', default=None, type=str,
                                 help='first day of the prediction (ex.: 01-01-2024; default: actual date)')
        self.parser.add_argument('-days', default=7, type=int,
                                 help=f'duration of the prediction in days (default: {7})') # TODO const
        self.parser.add_argument('--compare-mode', default=False,
                                 action='store_true', dest='c_mode',
                                 help='if it\'s set, the prediction will be safe in a spreadsheet (default: save to the database)')
        self.parser.add_argument('--update', default=False,
                                 action='store_true', dest='update',
                                 help='if it\'s set, when there\'s already a prediction in the same date range, it will be updated')
    
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
