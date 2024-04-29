from argparse import ArgumentParser
from app.model import Model
from utils.cmd import Command
from datetime import datetime
class RunPredictorCmd(Command):
    def __init__(self, model: Model):
        super().__init__('run-pred')
        self.model = model
    
    def set_parser(self, parser: ArgumentParser):
        super().set_parser(parser)
        parser.add_argument('id', choices=[pdt.id for pdt in self.model.pdts])
        parser.add_argument('-date', default=None, type=str)
        parser.add_argument('-days', default=7, type=int) # TODO const
    
    def run(self, args):
        date = datetime.now()
        if args.date is not None:
            try:
                date = datetime.strptime(args.date, '%d-%m-%Y')
            except ValueError:
                print('ERROR: -date invalid format')
                return
        self.model.run_predictor(args.id, date, args.days)