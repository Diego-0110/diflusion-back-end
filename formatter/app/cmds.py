from app.model import Model
from utils.cmd import Command

class FormatCommand(Command):
    def __init__(self, model: Model):
        super().__init__('format', 'format one or more types of data')
        self.model = model
        self.parser.add_argument('ids', choices=[f.data_id for f in self.model.fmts],
                                 nargs='+', help='types of data available')

    def run(self, args):
        self.model.format_data(args.ids)
        return 'Formater/s will be executed...'
