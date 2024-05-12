from app.model import Model
from recipes.controller import TemplateController
from utils.conn import ConnectionClosedError
from utils.cmd import Command, RunCmdError
from datetime import datetime, timedelta
from utils.conn import ConnsHandler

class SendCmd(Command):
    def __init__(self, model: Model, ctrl: TemplateController):
        super().__init__('send', 'send a command to another terminal')
        self.model = model
        self.ctrl = ctrl
        self.parser.add_argument('-id', choices=[c.id for c in self.model.ctrl_conns],
                                 required=True, help='id of the connection which the command will be sent to')
        self.parser.add_argument('--log-mode', default=False,
                                 action='store_true', dest='log_mode',
                                 help='if it\'s set, log mode is activated right before sending the command')
        self.parser.add_argument('-cmd', default=[], nargs='+', required=True,
                                 help='command to send')

    def run(self, args):
        cmd_str = ' '.join([*args.cmd, *args._rest])
        try:
            if args.log_mode:
                self.ctrl.terminal_mode = False
                self.ctrl.view.print_logs = True
            res = self.model.send_cmd(args.id, cmd_str)
            # Connection doesn't exist
            if res is None:
                raise RunCmdError(f'\'{args.id}\' doesn\'t exist')
            return res
        except ConnectionClosedError:
            raise RunCmdError(f'Connection \'{args.id}\' is closed')

class CronCmd(Command):
    def __init__(self, model: Model, ctrl: TemplateController):
        super().__init__('cron', 'executes a command at a certain time and optionally every x days')
        self.model = model
        self.ctrl = ctrl
        self.parser.add_argument('-dtime', required=True, type=str,
                                 help='day and time when the command will be executed (ex.: 01-01-2024-14:00)')
        self.parser.add_argument('-days', default=None, type=int,
                                 help='if it\'s specified, the command will be executed every <DAYS> days')
    
    def run(self, args):
        if args.days is not None and args.days < 1:
            raise RunCmdError('DAYS must be higher than 0')
        try:
            time_arg = datetime.strptime(args.dtime, '%d-%m-%Y-%H:%M')
        except ValueError:
            raise RunCmdError('-f should have the format dd-mm-YYYY-HH:MM')
        print('Insert the command to schedule:')
        cmd_list = input('> ').split()
        cmd_name = cmd_list[0]
        cmd_args_list = cmd_list[1:]
        if not cmd_list or '-h' in cmd_list or '--help' in cmd_list or cmd_name == self.id:
            raise RunCmdError(f'Invalid command:\n{self.ctrl.available_cmds()}')
        for cmd in self.ctrl.cmds:
            if cmd.id == cmd_name:
                try:
                    (args_c, rest) = cmd.parser.parse_known_intermixed_args(cmd_args_list)
                    args_c._rest = rest
                    def task_func():
                        args_c.func(args_c)
                    self.model.add_cron_task(task_func, time_arg,
                                             args.days and timedelta(days=args.days))
                    formatted_time = time_arg.strftime('%d %b, %Y - %H:%M')
                    if args.days is not None:
                        return f'Command will be executed on {formatted_time} every {args.days} day/s'
                    else:
                        return f'Command will be executed on {formatted_time}'
                except SystemExit:
                    raise RunCmdError(f'Invalid use of \'{cmd.id}\':\n{cmd.parser.format_help()}')
        raise RunCmdError(f'Select a valid command:\n{self.ctrl.available_cmds()}')




class ShowLogsCmd(Command):
    def __init__(self, model: Model):
        super().__init__('log')
        self.model = model
        self.parser.add_argument('-n', default=100)
        self.parser.add_argument('-t', default=[], nargs='+')
        self.parser.add_argument('-id', default=[], nargs='+')

    def run(self, args):
        return self.model.format_logs(args.n, args.t, args.id)
