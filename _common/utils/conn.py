import threading
import socket
import types
from .decorators import th_sf_singleton
class Connection:
    def __init__(self, id, host, port,
                 on_recv: types.FunctionType = None,
                 handle_event: types.FunctionType = lambda id, msg: msg,
                 handle_success: types.FunctionType = lambda id, msg: msg,
                 handle_error: types.FunctionType = lambda id, msg: msg):
        self.id = id
        self.host = host
        self.port = port
        self.on_recv = on_recv
        self.handle_event = handle_event
        self.handle_success = handle_success
        self.handle_error = handle_error
    
    def on_event(self, msg: str):
        self.handle_event(self.id, msg)
    
    def on_success(self, msg: str):
        self.handle_success(self.id, msg)

    def on_error(self, msg: str):
        self.handle_error(self.id, msg)

    def is_passive(self):
        return self.on_recv is not None

    def is_established(self):
        pass

    def get_status(self) -> str:
        pass

    def recv_loop(self):
        pass

    def start(self):
        pass

    def close(self):
        pass

    def restart(self):
        self.close()
        self.start()

    def try_send_msg(self, msg: str):
        pass

    def try_recv_msg(self) -> str:
        pass

class ConnectionClosedError(Exception):
    pass

class Client(Connection):
    def __init__(self, id, host, port, on_recv: types.FunctionType = None,
                 handle_event: types.FunctionType = lambda id, msg: msg,
                 handle_success: types.FunctionType = lambda id, msg: msg,
                 handle_error: types.FunctionType = lambda id, msg: msg):
        super().__init__(id, host, port, on_recv, handle_event, handle_success,
                         handle_error)
        self.sck: socket.socket = None
        self.sck_lock = threading.Lock()
    
    def is_established(self):
        return self.sck is not None
    
    def get_status(self) -> str:
        if self.is_established():
            return 'connected'
        else:
            return 'closed'

    def check_conn_loop(self):
        try:
            while True:
                if not self.sck.recv(1, socket.MSG_PEEK):
                    # Client manually closed or Server closed safely
                    self.sck_lock.acquire() # Wait if server was manually closed
                    if not self.is_established():
                        # Client manually closed
                        self.sck_lock.release()
                        raise OSError()
                    else:
                        # Server closed safely
                        self.sck_lock.release()
                        raise ConnectionAbortedError()
        except ConnectionResetError:
            # Abrupt close by server
            self.sck_lock.acquire() # Manual close while abrupt close
            self.sck = None
            self.sck_lock.release()
            self.on_error('Abrupt close by server')
        except (ConnectionAbortedError, AttributeError, OSError) as e:
            if isinstance(e, ConnectionAbortedError):
                # Server closed safely
                self.sck_lock.acquire() # Manual close while safe close
                self.sck = None
                self.sck_lock.release()
                self.on_event('Connection closed by server safely')
            else:
                # Client manually closed
                self.on_event('Connection manually closed')

    def recv_loop(self):
        while True:
            try:
                msg = self.try_recv_msg()
            except ConnectionClosedError:
                # Socket closed
                break
            self.on_recv(msg)

    def start(self):
        self.sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sck.connect((self.host, self.port))
            self.on_success('Successful connection')
            threading.Thread(target=self.check_conn_loop).start()
            if (self.is_passive()):
                threading.Thread(target=self.recv_loop).start()
        except (AttributeError, ConnectionRefusedError, OSError):
            # Client closed
            self.sck_lock.acquire() # Wait if server was manually closed
            if self.sck is None:
                # Manual close
                self.on_event('Client manually closed')
            else:
                # Unexpected close
                self.sck = None
                self.on_error('Connection refused')
            self.sck_lock.release()

    def close(self):
        self.sck_lock.acquire()
        # Wait if server closed and sck is being setting to None
        if self.is_established():
            self.sck.shutdown(socket.SHUT_RDWR)
            # shutdown -> OSError: only when close was called before
            self.sck.close()
            self.sck = None
        self.sck_lock.release()
    
    def try_send_msg(self, msg: str):
        try:
            self.sck.sendall(msg.encode())
            # AttributeError when Server is closed
        except (ConnectionResetError, ConnectionAbortedError, AttributeError,
                OSError):
            # Socket closed
            raise ConnectionClosedError()

    def try_recv_msg(self) -> str:
        # TODO arbitrary size of message
        try:
            raw_data = self.sck.recv(1024)
            # AttributeError when Server is closed
            if not raw_data: # Empty message: socket closed safely
                raise ConnectionClosedError()
            return raw_data.decode()
        except (ConnectionResetError, ConnectionAbortedError, AttributeError,
                OSError):
            # Socket closed
            raise ConnectionClosedError()

class Server(Connection):
    def __init__(self, id, host, port, on_recv: types.FunctionType = None,
                 handle_event: types.FunctionType = lambda id, msg: msg,
                 handle_success: types.FunctionType = lambda id, msg: msg,
                 handle_error: types.FunctionType = lambda id, msg: msg):
        super().__init__(id, host, port, on_recv, handle_event, handle_success, handle_error)
        self.sv_sck: socket.socket = None # Socket for server
        self.cl_sck: socket.socket = None # Socket for client connection
        self.cl_lock = threading.Lock()
        self.cl_evt = threading.Event() # When connection with client is closed
        self.sv_lock = threading.Lock()
    
    def is_established(self):
        return self.cl_sck is not None
    
    def is_listening(self):
        return self.sv_sck is not None
    
    def get_status(self) -> str:
        if self.is_established():
            return 'connected'
        elif self.is_listening():
            return 'listening'
        else:
            return 'closed'
    
    def check_conn_loop(self):
        try:
            while True:
                if not self.cl_sck.recv(1, socket.MSG_PEEK):
                    # Server manually closed or Client closed safely
                    self.cl_lock.acquire() # Wait if server was manually closed
                    if not self.is_established():
                        # Server manually closed
                        self.cl_lock.release()
                        raise OSError()
                    else:
                        # Client closed safely
                        self.cl_lock.release()
                        raise ConnectionAbortedError()

        except ConnectionResetError:
            # Abrupt close by client
            self.cl_lock.acquire() # Manual close while abrupt close
            self.cl_sck = None
            self.cl_evt.set()
            self.cl_lock.release()
            self.on_error('Abrupt close by client')
        except (ConnectionAbortedError, AttributeError, OSError) as e:
            # TODO BrokenPipeError
            if isinstance(e, ConnectionAbortedError):
                # Client closed safely
                self.cl_lock.acquire() # manual close while safe client close
                self.cl_sck = None
                self.cl_evt.set()
                self.cl_lock.release()
                self.on_event('Connection closed by client safely')
            else:
                # Server manually closed
                self.on_event('Connection manually closed')

    def recv_loop(self):
        while True:
            try:
                msg = self.try_recv_msg()
            except ConnectionClosedError:
                # Socket closed
                break
            self.on_recv(msg)
    
    def accept_loop(self):
        while True:
            try:
                # Race condition: manual close -> AttributeError
                self.cl_sck, addr = self.sv_sck.accept()
            except (AttributeError, OSError):
                # Server closed
                self.sv_lock.acquire() # Wait if server was manually closed
                if self.sv_sck is None:
                    # Manual close
                    self.on_event('Server manually closed')
                else:
                    # Unexpected close
                    self.sv_sck = None
                    self.on_error('Server closed unexpectedly')
                self.sv_lock.release()
                break
            self.on_success(f'Successful connection to client {addr}')
            threading.Thread(target=self.check_conn_loop).start()
            if self.is_passive():
                self.recv_loop()
            else:
                self.cl_evt.wait()
                self.cl_evt.clear()

    def start(self):
        self.sv_sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sv_sck.bind((self.host, self.port))
            self.sv_sck.listen()
            self.on_success('Server is listening')
            threading.Thread(target=self.accept_loop).start()
        except (AttributeError, OSError):
            # Server closed
            self.sv_lock.acquire() # Wait if server was manually closed
            if self.sv_sck is None:
                # Manual close
                self.on_event('Server manually closed')
            else:
                # Unexpected close
                self.sv_sck = None
                self.on_error('Connection refused')
            self.sv_lock.release()
    
    def close(self):
        self.cl_lock.acquire()
        # Wait if client closed and cl_sck is being setting to None
        if self.is_established():
            self.cl_sck.shutdown(socket.SHUT_RDWR)
            # shutdown -> OSError: only when close was called before
            self.cl_sck.close()
            self.cl_sck = None
            self.cl_evt.set()
        self.cl_lock.release()
        self.sv_lock.acquire() # Wait if server was unexpectedly closed
        if self.is_listening():
            # shutdown unnecesary when socket is used as server
            self.sv_sck.close()
            self.sv_sck = None
        self.sv_lock.release()
    
    def try_send_msg(self, msg: str):
        try:
            self.cl_sck.sendall(msg.encode())
            # AttributeError when Server is closed
        except (ConnectionResetError, ConnectionAbortedError, AttributeError,
                OSError):
            # Socket closed
            raise ConnectionClosedError()
    
    def try_recv_msg(self) -> str:
        # TODO arbitrary size of message
        try:
            raw_data = self.cl_sck.recv(1024)
            # AttributeError when Server is closed
            if not raw_data: # Empty message: socket closed safely
                raise ConnectionClosedError()
            return raw_data.decode()
        except (ConnectionResetError, ConnectionAbortedError, AttributeError,
                OSError):
            # Socket closed
            raise ConnectionClosedError()

@th_sf_singleton
class ConnsHandler:
    def __init__(self):
        self.conns: list[Connection] = []
        self.handle_event = lambda id, msg: msg
        self.handle_success = lambda id, msg: msg
        self.handle_error = lambda id, msg: msg
    
    def set_event_handler(self, handle_event: types.FunctionType):
        self.handle_event = handle_event
        for conn in self.conns:
            conn.handle_event = handle_event
    def set_success_handler(self, handle_success: types.FunctionType):
        self.handle_success = handle_success
        for conn in self.conns:
            conn.handle_success = handle_success
    def set_error_handler(self, handle_error: types.FunctionType):
        self.handle_error = handle_error
        for conn in self.conns:
            conn.handle_error = handle_error

    def add(self, conns: Connection | list[Connection]):
        conns_list = [conns] if isinstance(conns, Connection) else conns
        for conn in conns_list:
            self.conns.append(conn)
            conn.handle_event = self.handle_event
            conn.handle_success = self.handle_success
            conn.handle_error = self.handle_error

    def restart(self, ids: list[str] = []):
        if not ids: # restart all connections
            for conn in self.conns:
                conn.restart()
        else: # restart specified connections
            for conn in self.conns:
                if (conn.id in ids):
                    conn.restart()
    
    def close(self, ids: list[str] = []):
        if not ids: # restart all connections
            for conn in self.conns:
                conn.close()
        else: # restart specified connections
            for conn in self.conns:
                if (conn.id in ids):
                    conn.close()
    
    def get_conn(self, id: str) -> Connection | None:
        for conn in self.conns:
            if conn.id == id:
                return conn
        return None

    def get_status(self, ids: list[str] = [],
                   format: types.FunctionType = lambda id, st: f'{id}: {st}') -> str:
        status_list = []
        if not ids:
            for conn in self.conns:
                status_list.append(format(conn.id, conn.get_status()))
        else:
            for conn in self.conns:
                if conn.id in ids:
                    status_list.append(format(conn.id, conn.get_status()))
        return '\n'.join(status_list)
