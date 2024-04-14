import threading
import socket
import sys
import consts.config as config
from app.view import View
from utils.conn import ConnsHandler, Client
class Model:
    def __init__(self, view: View) -> None:
        self.view = view
        self.connsHandler = ConnsHandler()
        self.connsHandler.set_event_handler(lambda id, msg: self.view.on_action_start(f'{id}: {msg}'))
        self.connsHandler.set_success_handler(lambda id, msg: self.view.on_success(f'{id}: {msg}'))
        self.connsHandler.set_error_handler(lambda id, msg: self.view.on_error(f'{id}: {msg}'))
        self.connsHandler.add([
            Client('formatter_ctrl', config.FORMATTER_HOST,
                   config.FORMATTER_CTRL_PORT),
            Client('formatter_log', config.FORMATTER_HOST,
                   config.FORMATTER_LOG_PORT, self.handle_log),
            Client('daemon_ctrl', config.DAEMON_HOST,
                   config.DAEMON_CTRL_PORT),
            Client('daemon_log', config.DAEMON_HOST, config.DAEMON_LOG_PORT,
                   self.handle_log),
            Client('model_ctrl', config.MODEL_HOST,
                   config.MODEL_CTRL_PORT),
            Client('model_log', config.MODEL_HOST, config.MODEL_LOG_PORT,
                   self.handle_log)
            # Add connections
        ])
        # self.sck_daemon: socket = None
        # self.sck_model: socket = None
        output_id = self.view.add_output(sys.stdout)
        self.connsHandler.restart()
        self.view.rm_output(output_id)

    def handle_log(self, msg):
        print(msg)
        self.view.on_action_start(f'{msg}')

    def show_log(self, num_records: int, filter: list[str], origin: list[str]):
        self.view.show_log(num_records, filter, origin)
