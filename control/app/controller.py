from app.model import Model
from app.view import View
from app.cmds import ConnectionCmd, SendCmd, ShowLogsCmd, QuitCmd
from utils.cmd import CmdExecutor
from utils.conn import ConnsHandler

class Controller:
    # Receive inputs using the terminal.
    def __init__(self, model: Model, view: View):
        self.model = model
        self.view = view
        self.cmd_exec = CmdExecutor([
            ConnectionCmd(self.model),
            SendCmd(self.model),
            ShowLogsCmd(self.model),
            QuitCmd(self.model)
            # Add available commands
        ])
        self.terminal_mode = True

    def run(self):
        self.view.print_logs = True
        self.view.on_event('Starting...')
        conns = ConnsHandler()
        conns.restart()
        self.view.on_event('Running...')
        self.view.print_logs = False
        while True:
            if self.terminal_mode:
                input_str = input('control> ')
                if input_str == 'log':
                    self.terminal_mode = False
                    self.view.print_logs = True
                else:
                    self.cmd_exec.execute_cmd(input_str)
            else:
                input_str = input()
                if input_str == 'q':
                    self.terminal_mode = True
                    self.view.print_logs = False
