import consts.config as config
from loguru import logger
import os


class View:
    # TODO socket for logs from other modules
    def __init__(self) -> None:
        logger.add(os.path.join(config.LOG_PATH, 'logging.log'))
        # logger.add(self.process_str)
        # logger.info('a')

    def process_str(self, msg):
        print(f'Message: {msg}')

    def on_action_start(self, msg):
        logger.info(msg)

    def on_success(self, msg):
        logger.success(msg)

    def on_error(self, msg):
        logger.error(msg)

    def show_log(self, num_records: int, filter: list[str], origin: list[str]):
        print(f'num_records={num_records}, filter={filter}, origin={origin}')
        # TODO read from logs
