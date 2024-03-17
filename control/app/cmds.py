from app.model import Model
from utils.cmd import Command
from argparse import ArgumentParser
import os

# class Command:
#     def __init__(self, cmd_id: str, model: Model):
#         self.id = cmd_id
#         self.model = model

#     def set_parser(self, parser: ArgumentParser):
#         parser.set_defaults(func=self.run)

#     def run(self, args):
#         pass

class ConnectionCmd(Command):
    def __init__(self, model: Model):
        super().__init__('conn')
        self.model = model

    def status_func(self, args):
        self.model.connection_status()

    def restart_func(self, args):
        self.model.restart_connections(args.ids)

    def set_parser(self, parser: ArgumentParser):
        subparsers = parser.add_subparsers(required=True)
        status_parser = subparsers.add_parser('status')
        status_parser.set_defaults(func=self.status_func)
        restart_parser = subparsers.add_parser('restart')
        restart_parser.add_argument('-ids', default=[], nargs='+')
        restart_parser.set_defaults(func=self.restart_func)

class SendCmd(Command):
    def __init__(self, model: Model):
        super().__init__('send')
        self.model = model

    def set_parser(self, parser: ArgumentParser):
        super().set_parser(parser)
        parser.add_argument('id', choices=[conn.id for conn in self.model.conns])
        parser.add_argument('-cmd', default=[], nargs='+', required=True)

    def run(self, args):
        cmd_str = ' '.join(args.cmd)
        self.model.send_to(args.id, cmd_str)

class ShowLogsCmd(Command):
    def __init__(self, model: Model):
        super().__init__('log')
        self.model = model
    
    def set_parser(self, parser: ArgumentParser):
        """
        log (show last n lines)
        log -n 100 (show last 100 lines)
        log -id daemon (show last n lines from daemon)
        log -t info (show last n lines of informative logs)
        """
        super().set_parser(parser)
        parser.add_argument('-n', default=100)
        parser.add_argument('-t', default=[], nargs='+')
        parser.add_argument('-id', default=[], nargs='+')

    def run(self, args):
        self.model.show_log(args.n, args.t, args.id)

class QuitCmd(Command):
    def __init__(self, model: Model):
        super().__init__('quit') # TODO add alias
        self.model = model

    def run(self, args):
        for conn in self.model.conns:
            conn.close_conn()
        os._exit(1)
