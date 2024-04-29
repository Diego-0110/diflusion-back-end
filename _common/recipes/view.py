from loguru import logger
import sys
from utils.conn import ConnsHandler, Server, ConnectionClosedError

class ShareView:
    FORMAT = '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>'
    def __init__(self, log_file, log_host, log_port):
        self.print_logs = True
        logger.remove(0)
        logger.add(sys.stdout, format=ShareView.FORMAT,
                   filter=lambda x: self.print_logs)
        logger.add(log_file, format=ShareView.FORMAT)
        conns = ConnsHandler()
        conns.set_event_handler(lambda id, msg: self.on_event(f'{id}: {msg}', 1, False))
        conns.set_success_handler(lambda id, msg: self.on_success(f'{id}: {msg}', 1, False))
        conns.set_error_handler(lambda id, msg: self.on_error(f'{id}: {msg}', 1, False))
        self.server = Server('logs', log_host, log_port)
        conns.add(self.server)

        logger.add(self.server_log, format='{level}:{message}',
                   filter=lambda x: x['extra'].get('send'))
    
    def server_log(self, msg: str):
        try:
            self.server.try_send_msg(msg.rstrip()) # Remove \n
        except ConnectionClosedError: # Ignore error
            pass
    
    def on_event(self, msg: str, depth: int = 0, send: bool = True):
        logger.opt(depth=depth+1).info(msg, send=send)

    def on_success(self, msg: str, depth: int = 0, send: bool = True):
        logger.opt(depth=depth+1).success(msg, send=send)

    def on_error(self, msg: str, depth: int = 0, send: bool = True):
        logger.opt(depth=depth+1).error(msg, send=send)