import consts.config as config
import sys
import os
from utils.conn import ConnsHandler, Client
from loguru import logger

class View:
    FORMAT = '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>'
    N_CTRL = 'CONTROL'
    N_FORMATTER = 'FORMATTER'
    N_DAEMON = 'DAEMON'
    N_MODEL = 'MODEL'

    def __init__(self):
        self.print_logs = True
        logger.remove(0)
        logger.add(sys.stdout, format=View.FORMAT,
                   filter=lambda x: self.print_logs)
        logger.add(os.path.join(config.LOG_PATH, 'logging.log'), format=View.FORMAT)
        conns = ConnsHandler()
        conns.set_event_handler(lambda id, msg: self.on_event(f'{id}: {msg}', 1))
        conns.set_success_handler(lambda id, msg: self.on_success(f'{id}: {msg}', 1))
        conns.set_error_handler(lambda id, msg: self.on_error(f'{id}: {msg}', 1))
        conns.add([
            Client('formatter_log', config.FORMATTER_HOST,
                    config.FORMATTER_LOG_PORT, self.handle_log),
            Client('daemon_log', config.DAEMON_HOST, config.DAEMON_LOG_PORT,
                    self.handle_log),
            Client('model_log', config.MODEL_HOST, config.MODEL_LOG_PORT,
                    self.handle_log)
            # Add connections
        ])
    
    def handle_log(self, msg: str):
        msg_splitted = msg.split(':', 1)
        level = msg_splitted[0]
        message = msg_splitted[1]
        logger.log(level, message)
    
    def on_event(self, msg: str, depth: int = 0, tag: str = N_CTRL):
        logger.opt(depth=depth+1).info(msg, tag=tag)

    def on_success(self, msg: str, depth: int = 0, tag: str = N_CTRL):
        logger.opt(depth=depth+1).success(msg, tag=tag)

    def on_error(self, msg: str, depth: int = 0, tag: str = N_CTRL):
        logger.opt(depth=depth+1).error(msg, tag=tag)
