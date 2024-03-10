from app.model import Model
from app.view import View
from app.cmds import Command, ConnectionCmd, SendCmd, ShowLogsCmd
import argparse
class Controller:
    # Receive inputs using the terminal.
    def __init__(self, model: Model, view: View):
        self.model = model
        self.view = view
        self.cmds: list[Command] = [
            ConnectionCmd(self.model),
            SendCmd(self.model),
            ShowLogsCmd(self.model)
            # Command to schedule a message
            # Add available commands
        ]
        self.parser = argparse.ArgumentParser()
        self.subparsers = self.parser.add_subparsers()
        # Add all commands as subparsers
        for cmd in self.cmds:
            parser = self.subparsers.add_parser(cmd.id)
            cmd.set_parser(parser)
    
    def execute_cmd(self, str_cmd: str):
        # Parses str_cmd using the parser.
        try:
            args = self.parser.parse_args(str_cmd.split(' '))
            args.func(args)
        except SystemExit: # Avoid automatic exit from parser
            # TODO show error
            pass

    def run(self):
        while True:
            input_str = input('control> ')
            self.execute_cmd(input_str)
