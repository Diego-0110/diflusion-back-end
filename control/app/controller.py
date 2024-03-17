from app.model import Model
from app.view import View
from app.cmds import ConnectionCmd, SendCmd, ShowLogsCmd, QuitCmd
from utils.cmd import CmdExecutor
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
            # Command to schedule a message
            # Add available commands
        ])

    def run(self):
        while True:
            input_str = input('control> ')
            self.cmd_exec.execute_cmd(input_str)
