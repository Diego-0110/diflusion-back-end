from app.model import Model
from utils.cmd import Command

class UpdateCmd(Command):
    def __init__(self, model: Model):
        super().__init__('update', 'update one or more types of data')
        self.model = model
        self.parser.add_argument('ids', choices=[f.id for f in self.model.updts])
        self.parser.add_argument('--update-duplicates', default=False,
                                 action='store_true', dest='u_dups')
    
    def run(self, args):
        self.model.update_data(args.ids, args.u_dups)
        return 'Updater/s will be executed...'
