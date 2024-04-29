from app.model import Model
from argparse import ArgumentParser
from utils.cmd import Command

class UpdateCmd(Command):
    def __init__(self, model: Model):
        super().__init__('update')
        self.model = model

    def set_parser(self, parser: ArgumentParser):
        super().set_parser(parser)
        parser.add_argument('ids', choices=[f.data_id for f in self.model.updts])
    
    def run(self, args):
        self.model.update_data(args.ids)