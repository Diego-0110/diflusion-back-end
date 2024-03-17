import consts.config as config
import os
from utils.logger import Logger


class View(Logger):
    # TODO socket for logs from other modules
    def __init__(self) -> None:
        super().__init__([
            os.path.join(config.LOG_PATH, 'logging.log')
        ])

    def show_log(self, num_records: int, filter: list[str], origin: list[str]):
        print(f'num_records={num_records}, filter={filter}, origin={origin}')
        # TODO read from logs
