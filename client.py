import socket
import zlib
from threading import Thread
from time import sleep
import util
import os

from consts import PACKET_TYPE_START, PACKET_TYPE_END, ACK, FIN, REQUEST, MSG_TYPE_START, MSG_TYPE_END, NONE, \
    NO_FRAGMENT, FAIL, PROTOCOL_SIZE, CHECKSUM_LENGTH, FRAG_NUM_LENGTH, LOWEST_FRAGMENT_SIZE
from packet_factory import PacketFactory


class Client:

    def __init__(self, app):
        self.target_host = "127.0.0.1"
        self.target_port = 2222
        self.app = app
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client.settimeout(2)
        self.keep_connection_thread = True

    def keep_connection(self):
        while self.keep_connection_thread:
            msg = ACK + NONE + NO_FRAGMENT
            checksum = self.create_check_sum(msg)
            self.send(msg + checksum)
            sleep(5)

    def choose_port_host(self):
        while True:
            host = (input("[INPUT] Choose receiver host(default 127.0.0.1): "))
            if host == "":
                break
            else:
                if util.validate_ip_address(host):
                    self.target_host = host
                    break
                else:
                    print("[ERROR] Choose a valid IP adress")
        while True:
            port = (input("[INPUT] Choose receiver port(default 2222): "))
            if port == "":
                break
            else:
                if util.validate_port(port):
                    self.target_port = port
                    break
                else:
                    print("[ERROR] Choose a valid port")

    def create_check_sum(self, msg):
        checksum = zlib.crc32(msg).to_bytes(CHECKSUM_LENGTH, 'big')
        return checksum

    def initialize(self):
        remaining_tries = 3
        self.choose_port_host()
        while True:
            try:
                msg = REQUEST + NONE + NO_FRAGMENT
                checksum = self.create_check_sum(msg)
                self.send(msg + checksum)
                msg, addr = self.client.recvfrom(PROTOCOL_SIZE)
                if msg[PACKET_TYPE_START:PACKET_TYPE_END] != ACK:
                    print(msg[PACKET_TYPE_START:PACKET_TYPE_END])
                    if remaining_tries <= 0:
                        print(f'[CONNECTION] {self.target_host} is unreachable')
                        return
                    remaining_tries -= 1
                    print(f'[CONNECTION] Connection to {self.target_host} failed, remaining tries {remaining_tries}')
                    continue
                break
            except Exception:
                if remaining_tries <= 0:
                    print(f'[CONNECTION] {self.target_host} is unreachable')
                    self.app.connection_error()
                    return
                remaining_tries -= 1
                print(f'[CONNECTION] Connection to {self.target_host} failed, remaining tries {remaining_tries}')
                continue
        print(f'[CONNECTION] Connection to {self.target_host} established')
        self.connection_thread = Thread(target=self.keep_connection)
        self.connection_thread.start()
        self.create_msg()

    def send(self, msg):
        self.client.sendto(msg, (self.target_host, self.target_port))


    def close(self):
        self.keep_connection_thread = False
        self.connection_thread.join()
        header = REQUEST + FAIL + NO_FRAGMENT
        checksum = self.create_check_sum(header)
        self.send(header + checksum)

    def no_frag_transfer(self, packet):
        try:
            self.send(packet)
            msg, addr = self.client.recvfrom(PROTOCOL_SIZE)
            if msg[PACKET_TYPE_START:PACKET_TYPE_END] == ACK:
                respone = FIN + NONE + NO_FRAGMENT
                checksum = self.create_check_sum(respone)
                self.send(respone + checksum)
            else:
                self.no_frag_transfer(packet)
        except TimeoutError:
            self.no_frag_transfer(packet)

    def create_frag_num(self, num):
        frag = num.to_bytes(FRAG_NUM_LENGTH, 'big')
        return frag

    def frag_transfer(self, packets):
        index = 0
        msg_type = packets[0][MSG_TYPE_START:MSG_TYPE_END]
        while index != len(packets):
            try:
                self.send(packets[index])
                msg, addr = self.client.recvfrom(PROTOCOL_SIZE)
                msg = msg
                if msg[PACKET_TYPE_START:PACKET_TYPE_END] != ACK:
                    continue
                index += 1
            except TimeoutError:
                continue
        respone = FIN + msg_type + self.create_frag_num(len(packets) + 1)
        checksum = self.create_check_sum(respone)
        self.send(respone + checksum)

    def start_transfer(self, packets):
        if isinstance(packets, bytes):
            self.no_frag_transfer(packets)
        elif isinstance(packets, list):
            self.frag_transfer(packets)

    def create_msg(self):
        while True:
            msg_type = input("[INPUT] What type of message, file or text?(f/t): ")
            if util.validate_msg_type(msg_type):
                break
            print("[ERROR] Choose a valid message type")
        while True:
            fragment_size = input(
                f"[INPUT] What will be the fragment size?(default/max = {PROTOCOL_SIZE} bytes, lowest = {LOWEST_FRAGMENT_SIZE} bytes): ")
            if fragment_size == "":
                fragment_size = PROTOCOL_SIZE
                break
            if util.validate_fragment_size(fragment_size):
                break
            print("[ERROR] Choose a valid fragment size")
        if msg_type == 't':
            msg = input("[INPUT] Message you want to send: ")
            packets = PacketFactory(msg_type, int(fragment_size), msg=msg).create_txt_packets()
            self.start_transfer(packets)
        elif msg_type == "f":
            while True:
                file_path = input("File path: ")
                if util.validate_file_path(file_path):
                    break
                print("[ERROR] Choose a valid file path")
            file_name = os.path.basename(file_path)
            packets = PacketFactory(msg_type, int(fragment_size), file_name=file_name).create_file_packets()
            self.start_transfer(packets)
