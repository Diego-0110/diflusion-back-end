import consts.config as config
from app.view import View
from utils.conn import ConnsHandler, Client
from utils.exec import CronTaskExecutor
class Model:
    def __init__(self, view: View) -> None:
        self.view = view
        self.cron_task_exec = CronTaskExecutor()
        self.cron_task_exec.run()
        conns = ConnsHandler()
        conns.add([
            Client('formatter_ctrl', config.FORMATTER_HOST,
                    config.FORMATTER_CTRL_PORT),
            Client('daemon_ctrl', config.DAEMON_HOST,
                    config.DAEMON_CTRL_PORT),
            Client('model_ctrl', config.MODEL_HOST,
                    config.MODEL_CTRL_PORT),
            # Add connections
        ])
    
    def stop(self):
        self.cron_task_exec.stop()

    def show_log(self, num_records: int, filter: list[str], origin: list[str]):
        pass
