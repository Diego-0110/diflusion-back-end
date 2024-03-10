import threading
import socket
import types

# TODO connection handler

class Server:
    def __init__(self, id, host, port, handler: types.FunctionType = None):
        self.id = id
        self.host = host
        self.port = port
        self.sck: socket.socket = None
        self.client: socket.socket = None
        self.handler = handler

    def listen_thread(self):
        self.client, _ = self.sck.accept()
        if self.is_passive():
            while True:
                msg = self.recv_msg()
                if not msg:
                    break
                self.handler(msg)
                # TODO on close<

    def start(self):
        self.sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sck.bind((self.host, self.port))
            self.sck.listen()
            threading.Thread(target=self.listen_thread).start()
        except ConnectionError:
            self.sck = None
            raise ConnectionError

    def is_client(self):
        return self.client is not None
    
    def is_passive(self):
        return self.handler is not None

    def close_client(self):
        if self.is_client():
            self.client.close()
            self.client = None

    def close(self):
        self.close_client()
        if self.sck is not None:
            self.sck.close()
            self.sck = None

    def restart(self):
        self.close()
        self.start()

    # TODO on_close -> restart
    
    def send_msg(self, msg: str):
        if (not self.is_client()):
            raise ConnectionError()
        self.client.sendall(msg.encode())
    
    def recv_msg(self):
        if (not self.is_client()):
            raise ConnectionError()
        # TODO arbitrary size of message
        raw_data = self.client.recv(1024)
        return raw_data.decode()


class Client:
    # TODO handle disconnection
    def __init__(self, id, host, port, handler: types.FunctionType = None) -> None:
        self.id = id
        self.host = host
        self.port = port
        self.conn: socket.socket = None
        self.handler = handler
    
    def start_conn(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.conn.connect((self.host, self.port))
            if (self.is_passive()): # TODO see if there's a better way
                threading.Thread(target=self.listen).start()
            # if there is a ConnectionError, it lets raised
        except ConnectionError:
            self.conn = None
            raise ConnectionError

    def close_conn(self):
        if (self.is_connected()):
            self.conn.close()

    def restart_conn(self):
        self.close_conn()
        self.start_conn()

    def is_connected(self):
        return self.conn is not None
    
    def is_passive(self):
        return self.handler is not None
    
    def send_msg(self, msg: str):
        if (not self.is_connected()):
            raise ConnectionError()
        self.conn.sendall(msg.encode())
    
    def recv_msg(self):
        if (not self.is_connected()):
            raise ConnectionError()
        # TODO arbitrary size of message
        raw_data = self.conn.recv(1024)
        return raw_data.decode()

    def listen(self):
        while True:
            msg = self.recv_msg()
            if not msg:
                break
            self.handler(msg)