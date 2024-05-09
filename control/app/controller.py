from app.model import Model
from app.view import View
from app.cmds import SendCmd, CronCmd, ShowLogsCmd
from recipes.controller import TemplateController


class Controller(TemplateController):
    def __init__(self, model: Model, view: View):
        super().__init__('control', model, view, [
            SendCmd(model, self),
            CronCmd(model, self),
            ShowLogsCmd(model)
            # Add available commands
        ])
    
    def on_running(self):
        self.terminal_mode = True
        self.view.print_logs = False
