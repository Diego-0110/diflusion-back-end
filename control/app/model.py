import threading
import socket
import consts.config as config
from app.view import View
from utils.conn import Client
class Model:
    def __init__(self, view: View) -> None:
        self.view = view
        self.conns = [
            Client('formatter_ctrl', config.FORMATTER_HOST,
                   config.FORMATTER_CTRL_PORT),
            Client('formatter_log', config.FORMATTER_HOST,
                   config.FORMATTER_LOG_PORT, self.handle_log),
            Client('daemon_ctrl', config.DAEMON_HOST,
                   config.DAEMON_CTRL_PORT),
            Client('daemon_log', config.DAEMON_HOST, config.DAEMON_LOG_PORT,
                   self.handle_log)
            # Add connections
        ]
        self.sck_daemon: socket = None
        self.sck_model: socket = None
        self.restart_connections()

    def restart_connection(self, conn: Client):
        try:
            conn.restart_conn()
            self.view.on_success(f'Connection to {conn.id} stablished')
        except ConnectionError:
            self.view.on_error(f'Connection to {conn.id} refused')

    def restart_connections(self, ids: list[str] = []):
        if not ids: # restart all connections
            for conn in self.conns:
                self.restart_connection(conn)

        else: # restart specified connections
            for conn in self.conns:
                if (conn.id in ids):
                    self.restart_connection(conn)

    def connection_status(self):
        # Show if control terminal is connected to the rest of modules.
        for conn in self.conns:
            if conn.is_connected():
                print(f'{conn.id} is connected')
            else:
                print(f'{conn.id} is disconnected')

    def send_to(self, conn_id: str, msg):
        for conn in self.conns:
            if conn.id == conn_id:
                try:
                    conn.send_msg(msg)
                    self.view.on_success(f'Success sending msg to {conn.id}')
                    # TODO response
                except ConnectionError:
                    self.view.on_error(f'Fail sending msg to {conn.id}')
        # TODO handle when conn_id is not valid

    def handle_log(self, msg):
        print(msg)
        self.view.on_action_start(msg)

    def show_log(self, num_records: int, filter: list[str], origin: list[str]):
        self.view.show_log(num_records, filter, origin)
