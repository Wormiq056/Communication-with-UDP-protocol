import zlib
import socket
from consts import HEADER, PACKET_TYPE_START, PACKET_TYPE_END, ACK, FIN, REQUEST, DATA, \
    MSG_TYPE_START, MSG_TYPE_END, NONE, TXT, FILE, DATA, FRAG_NUM_START, FRAG_NUM_END, NO_FRAGMENT, CHECKSUM_START, \
    CHECKSUM_END, FAIL, PROTOCOL_SIZE, FORMAT


class Client:
    def __init__(self):
        self.target_host = "127.0.0.1"
        self.target_port = 2222
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def choose_port_host(self):
        host = (input("Choose target host(default 127.0.0.1): "))
        if host != "":
            self.target_host = host
        port = (input("Choose target port(default 2222): "))
        if port != "":
            self.target_port = port

    def create_check_sum(self, msg):
        checksum = zlib.crc32(bytes(msg))
        return str(checksum)

    def initialize(self):
        self.choose_port_host()
        msg = REQUEST + NONE + NO_FRAGMENT
        checksum = self.create_check_sum(msg)
        self.send(msg+checksum)
        self.client.recvfrom(PROTOCOL_SIZE)
        pass

    def send(self, msg):
        self.client.sendto(msg.encode(FORMAT), (self.target_host, self.target_port))
        pass

    def close(self):
        pass

    def create_msg(self):
        pass