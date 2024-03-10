from app.view import View
from app.model import Model
from utils.conn import Server
from app.cmds import Command, FormatCommand
import consts.config as config
import argparse

class Controller:
    def __init__(self, model, view) -> None:
        self.model = model
        self.view = view
        self.cmds: list[Command] = [
            FormatCommand(self.model)
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
        # TODO create socket for input
        ctrl_server = Server('Control', config.HOST, config.CTRL_PORT,
                             self.execute_cmd)
        ctrl_server.start()
        print('running')