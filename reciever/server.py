import socket
import threading
from time import sleep

from reciever.client_handler import ClientHandler
from helpers.consts import PROTOCOL_SIZE


class Server(threading.Thread):
    target_host: str
    target_port: int
    connections = {}
    active_connections = 0
    running = True

    def __init__(self, *args, **kwargs):
        super(Server, self).__init__(*args, **kwargs)
        self._stop = threading.Event()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.settimeout(1)

    def bind(self, host, port):
        self.target_host = host
        self.target_port = port
        self.server.bind((self.target_host, self.target_port))
        print("[SERVER] Listening on {} : {}".format(self.target_host, self.target_port))

    def revive(self):
        print("[SERVER] Listening on {} : {}".format(self.target_host, self.target_port))
        print(f'[SERVER] Active connections {self.active_connections}')
        self._stop.clear()

    def pause(self):
        print("[SERVER] Server has been paused")
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def create_client(self, msg, addr):
        print(f'[NEW CONNECTION] {addr} connected.')
        self.active_connections += 1
        print(f'[SERVER] Active connections {self.active_connections}')
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
            print(f'[SERVER] Active connections {self.active_connections}')

    def handle_client(self, msg, addr):
        client = self.connections.get(addr)
        client.process_packet(msg)

    def run(self):
        while self.running:
            try:
                if self.stopped():
                    sleep(0.5)
                    continue
                msg, addr = self.server.recvfrom(PROTOCOL_SIZE)
                if not self.connections.get(addr):
                    self.create_client(msg, addr)
                else:
                    self.handle_client(msg, addr)
            except TimeoutError:
                continue

    def send(self, msg, addr):
        self.server.sendto(msg, addr)

    def close(self):
        self.running = False