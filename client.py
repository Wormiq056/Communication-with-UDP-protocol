import zlib
import socket
from consts import HEADER_SIZE, PACKET_TYPE_START, PACKET_TYPE_END, ACK, FIN, REQUEST, DATA, \
    MSG_TYPE_START, MSG_TYPE_END, NONE, TXT, FILE, DATA, FRAG_NUM_START, FRAG_NUM_END, NO_FRAGMENT, CHECKSUM_START, \
    CHECKSUM_END, FAIL, PROTOCOL_SIZE, FORMAT
from packet_factory import PacketFactory
from threading import Thread
from time import sleep

class Client:

    def __init__(self):
        self.target_host = "127.0.0.1"
        self.target_port = 2222
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client.settimeout(1)
        self.keep_connection_thread = True

    def keep_connection(self):
        while self.keep_connection_thread:
            msg = ACK + NONE + NO_FRAGMENT
            checksum = self.create_check_sum(msg)
            self.send(msg+checksum)
            sleep(5)

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
        remaining_tries = 3
        self.choose_port_host()
        while True:
            try:
                msg = REQUEST + NONE + NO_FRAGMENT
                checksum = self.create_check_sum(msg)
                self.send(msg + checksum)
                msg , addr = self.client.recvfrom(PROTOCOL_SIZE)
                msg = msg.decode(FORMAT)
                if msg[PACKET_TYPE_START:PACKET_TYPE_END] != ACK:
                    print(msg[PACKET_TYPE_START:PACKET_TYPE_END])
                    remaining_tries -= 1
                    if remaining_tries < 0:
                        print(f'{self.target_host} is unreachable')
                        return

                    print(f'Connection to {self.target_host} failed, remaining tries {remaining_tries}')
                    continue
                break
            except TimeoutError:
                if remaining_tries < 0:
                    print(f'{self.target_host} is unreachable')
                    return
                remaining_tries -= 1
                print(f'Connection to {self.target_host} failed, remaining tries {remaining_tries}')
                continue
        print(f'Connection to {self.target_host} established')
        self.connection_thread = Thread(target=self.keep_connection)
        self.connection_thread.start()
        self.create_msg()

    def send(self, msg):
        self.client.sendto(msg.encode(FORMAT), (self.target_host, self.target_port))
        pass

    def close(self):
        self.keep_connection_thread = False
        self.connection_thread.join()
        header = REQUEST + FAIL + NO_FRAGMENT
        checksum = self.create_check_sum(header)
        self.send(header+checksum)


    def no_frag_transfer(self, packet):
        try:
            self.send(packet)
            msg, addr = self.client.recvfrom(PROTOCOL_SIZE)
            msg = msg.decode(FORMAT)

            if msg[PACKET_TYPE_START:PACKET_TYPE_END] == ACK:
                respone = FIN + NONE + NO_FRAGMENT
                checksum = self.create_check_sum(respone)
                self.send(respone + checksum)
            else:
                self.no_frag_transfer(packet)
        except TimeoutError:
            self.no_frag_transfer(packet)

    def create_frag_num(self, num):
        frag = str(num)
        while len(frag) != 5:
            frag = "0" + frag
        return frag

    def frag_transfer(self, packets):
        index = 0
        while len(packets) != 0:
            try:
                self.send(packets[index])
                msg, addr = self.client.recvfrom(PROTOCOL_SIZE)
                if msg[PACKET_TYPE_START:PACKET_TYPE_END] != "ACK":

                    continue
                index += 1
            except TimeoutError:
                continue
        respone = FIN + TXT + self.create_frag_num(len(packets) + 1)
        checksum = self.create_check_sum(respone)
        self.send(respone + checksum)

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
