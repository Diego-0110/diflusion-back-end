from utils.cmd import Command
from recipes.view import ShareView
from recipes.model import ShareModel
from utils.conn import ConnsHandler, Server, ConnectionClosedError
from utils.cmd import CmdExecutor, InvalidCmdError, HelpCmdError, RunCmdError
import os

class ConnectionCmd(Command):
    def __init__(self, ctrl):
        super().__init__('conn', 'show the status of the connections or restart one or more connections')
        self.ctrl = ctrl
        self.parser.add_argument('cmd', choices=['status', 'restart'])
        conns = ConnsHandler()
        self.parser.add_argument('-ids', default=[], nargs='+')

    def status_func(self, args) -> str:
        conns = ConnsHandler()
        return conns.get_status(args.ids,
                               lambda id, st: f'  {id + ':': <20}\t{st}')

    def restart_func(self, args):
        self.ctrl.view.print_logs = True
        conns = ConnsHandler()
        conns.restart(args.ids)
        self.ctrl.view.print_logs = False
        return None
    
    def run(self, args):
        if args.cmd == 'status':
            return self.status_func(args)
        elif args.cmd == 'restart':
            return self.restart_func(args)

class LogModeCmd(Command):
    def __init__(self, ctrl):
        super().__init__('log-mode', 'change to log mode (exit with \'q\')')
        self.ctrl = ctrl

    def run(self, args):
        self.ctrl.terminal_mode = False
        self.ctrl.view.print_logs = True
        return 'Log Mode active (exit with \'q\')'

class QuitCmd(Command):
    def __init__(self, model):
        super().__init__('quit', 'close this program safely')
        self.model = model

    def run(self, args):
        self.model.stop()
        conns = ConnsHandler()
        conns.close()
        os._exit(1)

class TemplateController(CmdExecutor):
    def __init__(self, name: str, model: ShareModel, view: ShareView, cmds: list[Command]):
        super().__init__([*cmds, ConnectionCmd(self), LogModeCmd(self), QuitCmd(model)])
        self.name = name
        self.model = model
        self.view = view
        self.terminal_mode = False

    def on_start(self):
        pass

    def on_running(self):
        pass

    def run(self):
        self.view.on_event('Starting...')
        self.on_start()
        conns = ConnsHandler()
        conns.restart()
        self.view.on_event('Running...')
        self.on_running()
        while True: # main thread should be active
            if self.terminal_mode:
                input_str = input(f'{self.name}> ')
                try:
                    cmd_res = self.execute_cmd(input_str)
                    if cmd_res is not None:
                        print(cmd_res)
                except RunCmdError as e:
                    print(f'ERROR: {e}')
                except (InvalidCmdError, HelpCmdError) as e:
                    print(e)
            else:
                input_str = input()
                if input_str == 'q':
                    self.terminal_mode = True
                    self.view.print_logs = False

class ShareController(TemplateController):
    def __init__(self, name: str, model: ShareModel, view: ShareView,
                 cmds: list[Command], ctrl_host: str, ctrl_port: int):
        super().__init__(name, model, view, cmds)
        self.ctrl_host = ctrl_host
        self.ctrl_port = ctrl_port

    def server_send_response(self, msg: str):
        try:
            conns = ConnsHandler()
            conns.get_conn('control').try_send_msg(msg)
        except ConnectionClosedError:
            pass

    def server_process_cmd(self, str_cmd: str):
        try:
            cmd_res = self.execute_cmd(str_cmd)
            if cmd_res is None:
                self.server_send_response('Command received and executed')
            else:
                self.server_send_response(cmd_res)
        except RunCmdError as e:
            self.server_send_response(str(e))
        except (InvalidCmdError, HelpCmdError) as e:
            self.server_send_response(str(e))
    
    def on_start(self):
        conns = ConnsHandler()
        ctrl_server = Server('control', self.ctrl_host, self.ctrl_port,
                             self.server_process_cmd)
        conns.add(ctrl_server)
