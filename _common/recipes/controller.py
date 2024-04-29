from utils.cmd import Command
from recipes.view import ShareView
from recipes.model import ShareModel
from utils.conn import ConnsHandler, Server, ConnectionClosedError
from utils.cmd import CmdExecutor, InvalidCmdError, HelpCmdError
import os

class QuitCmd(Command):
    def __init__(self, model: ShareModel):
        super().__init__('quit') # TODO add alias
        self.model = model

    def run(self, args):
        self.model.stop()
        conns = ConnsHandler()
        conns.close()
        os._exit(1)

class ShareController(CmdExecutor):
    def __init__(self, model: ShareModel, view: ShareView, cmds: list[Command],
                 ctrl_host, ctrl_port):
        super().__init__([*cmds, QuitCmd(model)])
        self.model = model
        self.view = view
        self.ctrl_host = ctrl_host
        self.ctrl_port = ctrl_port
        self.terminal_mode = False
    
    def server_send_response(self, msg: str):
        try:
            conns = ConnsHandler()
            conns.get_conn('Control').try_send_msg(msg)
        except ConnectionClosedError:
            pass

    def server_process_cmd(self, str_cmd: str):
        try:
            cmd_res = self.execute_cmd(str_cmd)
            self.server_send_response('Valid Command: Task added')
        except InvalidCmdError:
            self.server_send_response('Invalid Command')
        except HelpCmdError:
            self.server_send_response(self.parser.print_usage())

    def run(self):
        self.view.on_event('Starting...')
        conns = ConnsHandler()
        ctrl_server = Server('Control', self.ctrl_host, self.ctrl_port, self.server_process_cmd)
        conns.add(ctrl_server)
        conns.restart()
        self.view.on_event('Running...')
        while True: # main thread should be active
            if self.terminal_mode:
                input_str = input('terminal> ')
                if input_str == 'log':
                    self.terminal_mode = False
                    self.view.print_logs = True
                else:
                    try:
                        cmd_res = self.execute_cmd(input_str)
                    except InvalidCmdError:
                        pass
                    except HelpCmdError:
                        pass
            else:
                input_str = input()
                if input_str == 'q':
                    self.terminal_mode = True
                    self.view.print_logs = False
