import consts.config as config
from app.view import View
from utils.conn import ConnsHandler, Client
from utils.exec import CronTaskExecutor
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
    
    def stop(self):
        self.cron_task_exec.stop()

    def format_logs(self, num_records: int, filter: list[str], origin: list[str]) -> str:
        pass
