from argparse import ArgumentParser

class CustomArgumentParser(ArgumentParser):
    # Custom ArgumentParser that ignores _print_messag
    def _print_message(self, message, file=None):
        pass

class Command:
    def __init__(self, cmd_id: str, desc: str = None):
        self.id = cmd_id
        self.parser = CustomArgumentParser(prog=self.id, description=desc)
        self.parser.set_defaults(func=self.run)

    def run(self, args):
        pass

class InvalidCmdError(ValueError):
    pass

class HelpCmdError(ValueError):
    pass

class RunCmdError(Exception):
    pass

class CmdExecutor:
    def __init__(self, cmds: list[Command]) -> None:
        self.cmds = cmds
    
    def available_cmds(self):
        res = 'Available Cmds:'
        for cmd in self.cmds:
            if not cmd.parser.description:
                res += f'\n  {cmd.id}'
            else:
                res += f'\n  {cmd.id: <12}\t\t{cmd.parser.description}'
        res += f'\n  {'-h, --help':<12}\t\tshow this help message\n'
        return res

    def execute_cmd(self, str_cmd: str) -> str | None:
        # Parses str_cmd using the parser.
        cmd_list = str_cmd.split()
        if not cmd_list:
            raise InvalidCmdError(self.available_cmds())
        cmd_name = cmd_list[0]
        cmd_args_list = cmd_list[1:]
        if '-h' == cmd_name or '--help' == cmd_name:
            raise HelpCmdError(self.available_cmds())
        for cmd in self.cmds:
            if cmd.id == cmd_name:
                if '-h' in cmd_list or '--help' in cmd_list:
                    raise HelpCmdError(cmd.parser.format_help())
                try:
                    (args, rest) = cmd.parser.parse_known_intermixed_args(cmd_args_list)
                    args._rest = rest
                    return args.func(args)
                except RunCmdError as e:
                    raise e
                except SystemExit:
                    raise InvalidCmdError(cmd.parser.format_help())
        raise InvalidCmdError(self.available_cmds())
    