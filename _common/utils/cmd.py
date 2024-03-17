from argparse import ArgumentParser

class Command:
    def __init__(self, cmd_id: str):
        self.id = cmd_id

    def set_parser(self, parser: ArgumentParser):
        parser.set_defaults(func=self.run)

    def run(self, args):
        pass

class CmdExecutor:
    def __init__(self, cmds: list[Command]) -> None:
        self.cmds = cmds
        self.parser = ArgumentParser()
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

    