import consts.config as config
from loguru import logger
import os
from utils.conn import Server

class View:
    # TODO socket for logs from other modules
    def __init__(self) -> None:
        # logger.add(os.path.join(config.LOG_PATH, 'logging.log'))
        # logger.add(self.process_str)
        # logger.info('a')
        # TODO create sockets
        self.server = Server('logs', config.HOST, config.LOG_PORT)
        self.server.start()
        logger.add(self.process_str)

    def process_str(self, msg):
        try:
            self.server.send_msg(msg)
        except ConnectionError: # Ignore error
            pass

    def on_action_start(self, msg):
        logger.info(msg)

    def on_success(self, msg):
        logger.success(msg)

    def on_error(self, msg):
        logger.error(msg)