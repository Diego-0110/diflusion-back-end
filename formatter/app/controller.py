from app.model import Model
from app.view import View
from utils.cmd import CmdExecutor
from utils.conn import ConnsHandler, Server
from app.cmds import FormatCommand
import consts.config as config

class Controller:
    def __init__(self, model: Model, view: View) -> None:
        self.model = model
        self.view = view
        self.cmd_exec = CmdExecutor([
            FormatCommand(self.model)
            # Add available commands
        ])
    
    def run(self):
        # TODO input from terminal
        conns_handler = ConnsHandler()
        ctrl_server = Server('Control', config.HOST, config.CTRL_PORT,
                             self.cmd_exec.execute_cmd)
        conns_handler.add(ctrl_server)
        ctrl_server.start()
        print('running')
        while True:
            cmd = input()
            if cmd == 'q':
                conns_handler.close()
                break