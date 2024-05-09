import consts.config as config
from app.view import View
from utils.conn import ConnsHandler, Client, ConnectionClosedError
from utils.exec import CronTask, CronTaskExecutor
class Model:
    def __init__(self, view: View) -> None:
        self.view = view
        self.cron_task_exec = CronTaskExecutor()
        self.cron_task_exec.run()
        self.ctrl_conns = [
            Client('formatter', config.FORMATTER_HOST,
                    config.FORMATTER_CTRL_PORT),
            Client('daemon', config.DAEMON_HOST,
                    config.DAEMON_CTRL_PORT),
            Client('model', config.MODEL_HOST,
                    config.MODEL_CTRL_PORT),
            # Add connections
        ]
        conns = ConnsHandler()
        conns.add(self.ctrl_conns)
    
    def send_cmd(self, conn_id: str, cmd: str) -> str | None:
        conns = ConnsHandler()
        conn = conns.get_conn(conn_id)
        if conn is None:
            return None
        self.view.on_event(f'Sending \'{cmd}\' to \'{conn_id}\'')
        try:
            conn.try_send_msg(cmd)
            res = conn.try_recv_msg()
            self.view.on_success(f'\'{cmd}\' sent to \'{conn_id}\'')
            return res
        except ConnectionClosedError as e:
            self.view.on_error(f'Error while sending \'{cmd}\' to \'{conn_id}\': connection closed')
            raise e

    def add_cron_task(self, task, exec_time, time_delta):
        def try_task():
            try:
                task()
            except Exception as e:
                self.view.on_error(f'Error while executing a cron task: {e}')
        cron_task = CronTask(try_task, exec_time, time_delta)
        self.cron_task_exec.add_task(cron_task)

    def stop(self):
        self.cron_task_exec.stop()

    def format_logs(self, num_records: int, filter: list[str], origin: list[str]) -> str:
        pass
