import consts.config as config
import os
from utils.logger import Logger
from utils.conn import ConnsHandler, Server, ConnectionClosedError

class View(Logger):
    def __init__(self):
        super().__init__([
            self.process_str
        ])
        self.connsHandler = ConnsHandler()
        self.connsHandler.set_event_handler(lambda id, msg: self.on_action_start(f'{id}: {msg}'))
        self.connsHandler.set_success_handler(lambda id, msg: self.on_success(f'{id}: {msg}'))
        self.connsHandler.set_error_handler(lambda id, msg: self.on_error(f'{id}: {msg}'))
        self.server = Server('logs', config.HOST, config.LOG_PORT)
        self.connsHandler.add(self.server)
        self.server.start()

    def process_str(self, msg):
        try:
            self.server.try_send_msg(msg)
        except ConnectionClosedError: # Ignore error
            pass
