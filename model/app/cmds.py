from argparse import ArgumentParser
from app.model import Model
from utils.cmd import Command

class RunPredictorCmd(Command):
    def __init__(self, model: Model):
        super().__init__('run-pred')
        self.model = model
    
    def set_parser(self, parser: ArgumentParser):
        super().set_parser(parser)
        parser.add_argument('id')
    
    def run(self, args):
        self.model.run_predictor(args.id)