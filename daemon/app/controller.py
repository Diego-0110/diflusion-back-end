from app.view import View
from app.model import Model
from utils.conn import ConnsHandler, Server
from utils.cmd import CmdExecutor
from app.cmds import UpdateCmd
import consts.config as config

class Controller:
    def __init__(self, model: Model, view: View) -> None:
        self.model = model
        self.view = view
        self.cmd_exec = CmdExecutor([
            UpdateCmd('update', model)
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
        while True: # main thread should be active
            cmd = input()
            if cmd == 'q':
                self.model.task_exec.stop()
                conns_handler.close()
                break