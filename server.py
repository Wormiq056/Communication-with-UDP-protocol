import socket
import threading
import sys
import time
import consts
from client_handler import ClientHandler


class Server(threading.Thread):
    TARGET_HOST = "127.0.0.1"
    TARGET_PORT = 2222

    def __init__(self, *args, **kwargs):
        super(Server, self).__init__(*args, **kwargs)
        self._stop = threading.Event()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.TARGET_HOST, self.TARGET_PORT))
        self.server.settimeout(1)
        print("Listening on {} : {} (default)".format(self.TARGET_HOST, self.TARGET_PORT))

    def revive(self):
        print("Listening on {} : {} (default)".format(self.TARGET_HOST, self.TARGET_PORT))
        self._stop.clear()

    def pause(self):
        print("Server has been paused")
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def handle_client(self, conn, addr):
        print(f'[NEW CONNECTION] {addr} connected.')
        # connected = True
        # conn.settimeout(1)
        #
        # while connected:
        #     header_msg = conn.recv(consts.HEADER).decode(consts.FORMAT)
        ClientHandler(conn, addr)

    def run(self):
        self.server.listen()
        while True:
            try:
                if self.stopped():
                    time.sleep(0.5)
                    continue
                conn, addr = self.server.accept()

                thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                thread.start()
            except TimeoutError:
                continue

    def close(self):
        print('test')
        sys.exit()
