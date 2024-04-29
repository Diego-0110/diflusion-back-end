from app.model import Model
from utils.conn import ConnectionClosedError
from utils.cmd import Command
from utils.exec import CronTask
from argparse import ArgumentParser
from datetime import datetime, timedelta
from utils.conn import ConnsHandler
import os

class ConnectionCmd(Command):
    def __init__(self, model: Model):
        super().__init__('conn')
        self.model = model

    def status_func(self, args):
        conns = ConnsHandler()
        print(conns.get_status())
        return 'aaa'

    def restart_func(self, args):
        self.model.view.print_logs = True
        conns = ConnsHandler()
        conns.restart(args.ids)
        self.model.view.print_logs = False

    def set_parser(self, parser: ArgumentParser):
        subparsers = parser.add_subparsers(required=True)
        status_parser = subparsers.add_parser('status')
        status_parser.set_defaults(func=self.status_func)
        restart_parser = subparsers.add_parser('restart')
        restart_parser.add_argument('-ids', default=[], nargs='+')
        restart_parser.set_defaults(func=self.restart_func)

class SendCmd(Command):
    def __init__(self, model: Model):
        super().__init__('send')
        self.model = model

    def set_parser(self, parser: ArgumentParser):
        super().set_parser(parser)
        parser.add_argument('id')
        parser.add_argument('-t', default=None, type=str)
        parser.add_argument('-d', default=None, type=int)
        parser.add_argument('-cmd', default=[], nargs='+', required=True)

    def run(self, args):
        cmd_str = ' '.join(args.cmd)
        conns = ConnsHandler()
        conn = conns.get_conn(args.id)
        # Check connection exists
        if conn is None:
            print(f'ERROR: \'{args.id}\' doesn\'t exist')
            return
        # Send with a scheduler
        if args.t is not None or args.d is not None:
            if args.d is not None and args.d < 1:
                print('ERROR: -d must be higher than 0')
                return
            time_arg = datetime.now()
            if isinstance(args.t, str):
                try:
                    time_arg = datetime.strptime(args.t, '%d-%m-%Y-%H:%M')
                except ValueError:
                    print('ERROR: -f invalid format')
                    return
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
                print(f'SUCCESS: cmd will be sent on {formatted_time} every {args.d} days')
            else:
                print(f'SUCCESS: cmd will be sent on {formatted_time}')
        else: # Send inmediately
            try:
                conn.try_send_msg(cmd_str)
                print(conn.try_recv_msg())
            except ConnectionClosedError:
                print(f'ERROR: {conn.id} is closed')

class ShowLogsCmd(Command):
    def __init__(self, model: Model):
        super().__init__('log')
        self.model = model
    
    def set_parser(self, parser: ArgumentParser):
        """
        log (show last n lines)
        log -n 100 (show last 100 lines)
        log -id daemon (show last n lines from daemon)
        log -t info (show last n lines of informative logs)
        """
        super().set_parser(parser)
        parser.add_argument('-n', default=100)
        parser.add_argument('-t', default=[], nargs='+')
        parser.add_argument('-id', default=[], nargs='+')

    def run(self, args):
        self.model.show_log(args.n, args.t, args.id)

class QuitCmd(Command):
    def __init__(self, model: Model):
        super().__init__('quit') # TODO add alias
        self.model = model

    def run(self, args):
        conns = ConnsHandler()
        conns.close()
        self.model.cron_task_exec.stop()
        os._exit(1)
