from app.model import Model
from utils.conn import ConnectionClosedError
from utils.cmd import Command, RunCmdError
from utils.exec import CronTask
from datetime import datetime, timedelta
from utils.conn import ConnsHandler

class SendCmd(Command):
    def __init__(self, model: Model, ctrl):
        super().__init__('send', 'send a command to a connection with the option of specify the T time (default: time now) and the frequency D days (default: not repeat)')
        self.model = model
        self.ctrl = ctrl
        self.parser.add_argument('-id', choices=[c.id for c in self.model.ctrl_conns],
                                 required=True)
        self.parser.add_argument('-t', default=None, type=str)
        self.parser.add_argument('-d', default=None, type=int)
        self.parser.add_argument('--log-mode', default=False,
                                 action='store_true', dest='log_mode')
        self.parser.add_argument('-cmd', default=[], nargs='+', required=True)

    def run(self, args):
        cmd_str = ' '.join(args.cmd)
        conns = ConnsHandler()
        conn = conns.get_conn(args.id)
        # Check connection exists
        if conn is None:
            raise RunCmdError(f'\'{args.id}\' doesn\'t exist')
        # Send with a scheduler
        if args.t is not None or args.d is not None:
            if args.d is not None and args.d < 1:
                raise RunCmdError('-d must be higher than 0')
            time_arg = datetime.now()
            if isinstance(args.t, str):
                try:
                    time_arg = datetime.strptime(args.t, '%d-%m-%Y-%H:%M')
                except ValueError:
                    raise RunCmdError('-f should have the format dd-mm-YYYY-HH:MM')
            def send_func():
                try:
                    conn.try_send_msg(cmd_str)
                    conn.try_recv_msg()
                except ConnectionClosedError:
                    pass
            cron_task = CronTask(send_func, time_arg,
                                    args.d and timedelta(days=args.d))
            self.model.cron_task_exec.add_task(cron_task)
            formatted_time = time_arg.strftime('%d %b, %Y - %H:%M')
            if args.d is not None:
                return f'cmd will be send on {formatted_time} every {args.d} days'
            else:
                return f'cmd will be send on {formatted_time}'
        else: # Send inmediately
            try:
                if args.log_mode:
                    self.ctrl.terminal_mode = False
                    self.ctrl.view.print_logs = True
                conn.try_send_msg(cmd_str)
                return conn.try_recv_msg()
            except ConnectionClosedError:
                raise RunCmdError(f'{conn.id} is closed')

class ShowLogsCmd(Command):
    def __init__(self, model: Model):
        super().__init__('log')
        self.model = model
        self.parser.add_argument('-n', default=100)
        self.parser.add_argument('-t', default=[], nargs='+')
        self.parser.add_argument('-id', default=[], nargs='+')

    def run(self, args):
        return self.model.format_logs(args.n, args.t, args.id)
