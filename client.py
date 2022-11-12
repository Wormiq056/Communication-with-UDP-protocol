import zlib
import socket
from consts import HEADER_SIZE, PACKET_TYPE_START, PACKET_TYPE_END, ACK, FIN, REQUEST, DATA, \
    MSG_TYPE_START, MSG_TYPE_END, NONE, TXT, FILE, DATA, FRAG_NUM_START, FRAG_NUM_END, NO_FRAGMENT, CHECKSUM_START, \
    CHECKSUM_END, FAIL, PROTOCOL_SIZE, FORMAT
from packet_factory import PacketFactory


class Client:
    def __init__(self):
        self.target_host = "127.0.0.1"
        self.target_port = 2222
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client.settimeout(2000)

    def choose_port_host(self):
        host = (input("Choose target host(default 127.0.0.1): "))
        if host != "":
            self.target_host = host
        port = (input("Choose target port(default 2222): "))
        if port != "":
            self.target_port = port

    def create_check_sum(self, msg):
        checksum = zlib.crc32(msg.encode(FORMAT))
        return str(checksum)

    def initialize(self):
        self.choose_port_host()
        msg = REQUEST + NONE + NO_FRAGMENT
        checksum = self.create_check_sum(msg)
        self.send(msg + checksum)
        self.client.recvfrom(PROTOCOL_SIZE)
        self.create_msg()

    def send(self, msg):
        self.client.sendto(msg.encode(FORMAT), (self.target_host, self.target_port))
        pass

    def close(self):
        pass

    def no_frag_transfer(self, packets):

        self.send(packets)
        msg, addr = self.client.recvfrom(PROTOCOL_SIZE)
        msg = msg.decode(FORMAT)
        print(msg)
        if msg[PACKET_TYPE_START:PACKET_TYPE_END] == ACK:
            respone = FIN + NONE + NO_FRAGMENT
            checksum = self.create_check_sum(respone)
            self.send(respone + checksum)
        else:
            self.no_frag_transfer(packets)


    def frag_transfer(self, packets):
        pass

    def start_transfer(self, packets):
        if isinstance(packets, str):
            self.no_frag_transfer(packets)
        elif isinstance(packets, list):
            self.frag_transfer(packets)

    def create_msg(self):
        msg_type = input("What type of message, file or text?(f/t): ")
        fragment_size = input("What will be the fragment size?(default and max 1400): ")
        if fragment_size == "":
            fragment_size = PROTOCOL_SIZE
        if msg_type == 't':
            msg = input("Message: ")
            packets = PacketFactory(msg_type, fragment_size, msg=msg).create_txt_packets()
            self.start_transfer(packets)
        elif msg_type == "f":
            file_name = input("File path: ")
        pass
