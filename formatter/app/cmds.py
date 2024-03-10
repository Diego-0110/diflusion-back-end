from app.model import Model
from argparse import ArgumentParser

class Command:
    def __init__(self, cmd_id: str, model: Model):
        self.id = cmd_id
        self.model = model

    def set_parser(self, parser: ArgumentParser):
        parser.set_defaults(func=self.run)

    def run(self, args):
        pass


class FormatCommand(Command):
    def __init__(self, model: Model):
        super().__init__('format', model)

    def set_parser(self, parser: ArgumentParser):
        super().set_parser(parser)
        parser.add_argument('ids', choices=[f.data_id for f in self.model.fmts])

    def run(self, args):
        self.model.format_data(args.ids)
