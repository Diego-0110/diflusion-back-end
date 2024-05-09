from recipes.controller import ShareController
from app.model import Model
from app.view import View
from app.cmds import FormatCommand
import consts.config as config

class Controller(ShareController):
    def __init__(self, model: Model, view: View):
        super().__init__('formatter', model, view, [
            FormatCommand(model)
            # Add available commands
        ], config.HOST, config.CTRL_PORT)
