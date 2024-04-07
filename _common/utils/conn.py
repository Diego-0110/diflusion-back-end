import threading
import socket
import types

class Connection:
    def __init__(self, id, host, port,
                 on_recv: types.FunctionType = None,
                 on_info: types.FunctionType = lambda id, msg: msg,
                 on_success: types.FunctionType = lambda id, msg: msg,
                 on_error: types.FunctionType = lambda id, msg: msg):
        self.id = id
        self.host = host
        self.port = port
        self.on_recv = on_recv
        self.on_info = lambda msg: on_info(self.id, msg)
        self.on_success = lambda msg: on_success(self.id, msg)
        self.on_error = lambda msg: on_error(self.id, msg)

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
                 on_info: types.FunctionType = lambda id,msg: msg,
                 on_success: types.FunctionType = lambda id, msg: msg,
                 on_error: types.FunctionType = lambda id, msg: msg):
        super().__init__(id, host, port, on_recv, on_info, on_success, on_error)
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
            self.sck_sck = None
            self.sck_lock.release()
            self.on_error('Abrupt close by server')
        except (ConnectionAbortedError, AttributeError, OSError) as e:
            if isinstance(e, ConnectionAbortedError):
                # Server closed safely
                self.sck_lock.acquire() # Manual close while safe close
                self.sck_sck = None
                self.sck_lock.release()
                self.on_info('Connection closed by server safely')
            else:
                # Client manually closed
                self.on_info('Connection manually closed')

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
                self.on_info('Client manually closed')
            else:
                # Unexpected close
                self.sck = None
                self.on_error('Client closed unexpectedly')
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
                 on_info: types.FunctionType = lambda id, msg: msg,
                 on_success: types.FunctionType = lambda id, msg: msg,
                 on_error: types.FunctionType = lambda id, msg: msg):
        super().__init__(id, host, port, on_recv, on_info, on_success, on_error)
        self.sv_sck: socket.socket = None # Socket for server
        self.cl_sck: socket.socket = None # Socket for client connection
        self.cl_lock = threading.Lock()
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
            self.cl_lock.release()
            self.on_error('Abrupt close by client')
        except (ConnectionAbortedError, AttributeError, OSError) as e:
            # TODO BrokenPipeError
            if isinstance(e, ConnectionAbortedError):
                # Client closed safely
                self.cl_lock.acquire() # manual close while safe client close
                self.cl_sck = None
                self.cl_lock.release()
                self.on_info('Connection closed by client safely')
            else:
                # Server manually closed
                self.on_info('Connection manually closed')

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
                self.cl_sck, addr = self.sv_sck.accept() # TODO IP
            except (AttributeError, OSError):
                # Server closed
                self.sv_lock.acquire() # Wait if server was manually closed
                if self.sv_sck is None:
                    # Manual close
                    self.on_info('Server manually closed')
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
                while self.is_established(): pass

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
                self.on_info('Server manually closed')
            else:
                # Unexpected close
                self.sv_sck = None
                self.on_error('Server closed unexpectedly')
            self.sv_lock.release()
    
    def close(self):
        self.cl_lock.acquire()
        # Wait if client closed and cl_sck is being setting to None
        if self.is_established():
            self.cl_sck.shutdown(socket.SHUT_RDWR)
            # shutdown -> OSError: only when close was called before
            self.cl_sck.close()
            self.cl_sck = None
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

class ConnsHandler:
    # TODO conns status, send, recv
    def __init__(self, conns: list[Server | Client],
                 on_success: types.FunctionType,
                 on_error: types.FunctionType) -> None:
        self.conns: list[Server | Client] = conns
        self.on_success = on_success
        self.on_error = on_error

    def _restart_conn(self, conn: Client | Server):
        try:
            conn.restart_conn()
            self.on_success(conn.id)
        except ConnectionError:
            self.on_error(conn.id)

    def restart_conns(self, ids: list[str] = []):
        if not ids: # restart all connections
            for conn in self.conns:
                self._restart_conn(conn)
        else: # restart specified connections
            for conn in self.conns:
                if (conn.id in ids):
                    self._restart_conn(conn)
