from recipes.controller import ShareController
from app.view import View
from app.model import Model
from app.cmds import RunPredictorCmd
import consts.config as config

class Controller(ShareController):
    def __init__(self, model: Model, view: View):
        super().__init__('model', model, view, [
            RunPredictorCmd(model)
            # Add available commands
        ], config.HOST, config.CTRL_PORT)
