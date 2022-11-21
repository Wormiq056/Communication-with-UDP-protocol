import socket
import threading
from time import sleep

from helpers.consts import PROTOCOL_SIZE, DOWNLOAD_PATH
from reciever.client_handler import ClientHandler
from helpers import util


class Server(threading.Thread):
    """
    class which acts as a server and receives packets, based on current connected clients handles messages
    this class also runs on its own thread
    """
    target_host: str
    target_port: int
    connections = {}
    active_connections = 0
    running = True
    program_interface = None
    download_path = DOWNLOAD_PATH

    def __init__(self) -> None:
        super(Server, self).__init__()
        self._stop = threading.Event()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.settimeout(1)

    def bind(self, host: str, port: int, interface) -> None:
        """
        method that binds server to given IP and port and also passes pointer to ProgramInterface
        """
        self.target_host = host
        self.target_port = port
        self.server.bind((self.target_host, self.target_port))
        self.program_interface = interface
        print("[SERVER] Listening on {} : {}".format(self.target_host, self.target_port))

    def revive(self) -> None:
        """
        method that is used when server was stopped(it not listening) to have it listen again
        """
        print("[SERVER] Listening on {} : {}".format(self.target_host, self.target_port))
        self._stop.clear()

    def pause(self) -> None:
        """
        method that is called when we want to pause listening of server
        """
        print("[SERVER] Server has been paused")
        self._stop.set()

    def stopped(self) -> bool:
        """
        method that checks if server is paused or running
        """
        return self._stop.is_set()

    def create_client(self, msg: bytes, addr: tuple) -> None:
        """
        method that creates new client if IP and port have not been connected yet
        it creates another thread that will wait for connection packets in order to hold connection
        and also stores client in dictionary
        :param msg: received packet
        :param addr: address origin
        """
        print(f'[NEW CONNECTION] {addr} connected.')
        self.active_connections += 1
        print(f'[SERVER] Active connections {self.active_connections}')
        new_client = ClientHandler(addr, self)
        thread = threading.Thread(target=new_client.hold_connection)
        thread.start()
        self.connections[addr] = new_client
        new_client.process_packet(msg)

    def remove_connection(self, addr: tuple) -> None:
        """
        method that is called when client closes connection or when server does not receive connection packets
        indicating that client wants to stay connected, meaning it will remove it's client handler
        :param addr: address to remove
        """
        if self.connections[addr] and self.running:
            self.active_connections -= 1
            self.connections[addr] = None
            print(f'[DISCONNECTED] {addr}.')
            print(f'[SERVER] Active connections {self.active_connections}')

    def handle_client(self, msg: bytes, addr: tuple) -> None:
        """
        method that is called when server receives a packet for client that is already connected
        :param msg: packet in bytes
        :param addr: address of client
        """
        client = self.connections.get(addr)
        client.process_packet(msg)

    def run(self) -> None:
        """
        main listen method of server that waits for packet and sends it to corresponding client handler
        """
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
            except ConnectionResetError:
                self.close()
                self.program_interface.server_error()

    def send(self, msg: bytes, addr: tuple) -> None:
        """
        helper method that sends given packet to given address
        :param msg: packet you want to send
        :param addr: address you want to send to
        """
        self.server.sendto(msg, addr)

    def close(self) -> None:
        """
        method that is used when we want to exit program or when error has occurred
        """
        self.running = False

    def change_download_path(self) -> None:
        """
        method that is called when we want to change receiver download path
        """
        while True:
            download_path = input("[INPUT] New download path: ")
            if not util.validate_download_path(download_path):
                print("[ERROR] Invalid download path")
                continue
            if download_path == "":
                print(f"[INFO] Download was not changed: {self.download_path}")
                break
            if download_path[-1] != "/":
                download_path += "/"

            self.download_path = download_path
            print(f"[INFO] Download changed to: {self.download_path}")
