import socket
import threading
from time import sleep
from consts import FORMAT, PROTOCOL_SIZE
from client_handler import ClientHandler


class Server(threading.Thread):
    TARGET_HOST = "127.0.0.1"
    TARGET_PORT = 2222
    connections = {}
    active_connections = 0

    def __init__(self, *args, **kwargs):
        super(Server, self).__init__(*args, **kwargs)

        self._stop = threading.Event()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind((self.TARGET_HOST, self.TARGET_PORT))
        self.server.settimeout(1)
        print("[INFO] Listening on {} : {} (default)".format(self.TARGET_HOST, self.TARGET_PORT))

    def revive(self):
        print("[INFO] Listening on {} : {} (default)".format(self.TARGET_HOST, self.TARGET_PORT))
        self._stop.clear()

    def pause(self):
        print("[INFO] Server has been paused")
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def create_client(self, msg, addr):
        print(f'[NEW CONNECTION] {addr} connected.')
        self.active_connections += 1
        print(f'[INFO] Active connections {self.active_connections}')

        new_client = ClientHandler(addr, self)
        thread = threading.Thread(target=new_client.hold_connection)
        thread.start()
        self.connections[addr] = new_client
        new_client.process_packet(msg)

    def remove_connection(self, addr):
        if self.connections[addr]:
            self.active_connections -= 1
            self.connections[addr] = None
            print(f'[DISCONNECTED] {addr}.')
            print(f'[INFO] Active connections {self.active_connections}')

    def handle_client(self, msg, addr):
        client = self.connections.get(addr)
        client.process_packet(msg)

    def run(self):
        while True:
            try:
                if self.stopped():
                    sleep(0.5)
                    continue
                msg, addr = self.server.recvfrom(PROTOCOL_SIZE)
                if not self.connections.get(addr):
                    self.create_client(msg.decode(FORMAT), addr)
                else:
                    self.handle_client(msg.decode(FORMAT), addr)
            except TimeoutError:
                continue

    def send(self, msg, addr):
        self.server.sendto(msg.encode(FORMAT), addr)
