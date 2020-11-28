import pickle
import socket
import Queue


def run_async(func):
	from threading import Thread
	from functools import wraps

	@wraps(func)
	def async_func(*args, **kwargs):
		func_hl = Thread(target = func, args = args, kwargs = kwargs)
		func_hl.start()
		return func_hl

	return async_func


class CClient:
    def __init__(self, tcp_ip, tcp_port):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((tcp_ip, tcp_port))

    @run_async
    def ethernet_send(self, data):
        data_to_send = pickle.dumps(data)
        self._socket.send(data_to_send)

class CServer:
    def __init__(self, tcp_ip, tcp_port):
        self._recv_queue = Queue.Queue()

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind((tcp_ip, tcp_port))
        self._socket.listen(1)
        self._conn, self._addr = self._socket.accept()
        print("[SERVER] Client connected with addr: {0}".format(self._addr))

    def get_recv_data(self):
        return self._recv_queue.get()


    @run_async
    def ethernet_start_recv(self):
        while True:
            data = self._conn.recv(8096)
            list_data = pickle.loads(data)
            self._recv_queue.put(list_data)