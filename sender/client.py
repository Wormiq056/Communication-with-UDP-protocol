import os
import socket
from threading import Thread
from time import sleep

from helpers import util
from helpers.consts import PACKET_TYPE_START, PACKET_TYPE_END, ACK, FIN, REQUEST, MSG_TYPE_START, MSG_TYPE_END, NONE, \
    NO_FRAGMENT, FAIL, PROTOCOL_SIZE, LOWEST_FRAGMENT_SIZE, TXT, FRAG_NUM_START, FRAG_NUM_END, SLIDING_WINDOW_SIZE
from sender.packet_factory import PacketFactory


class Client:
    connection_thread: Thread

    def __init__(self, app):
        self.target_host = "127.0.0.1"
        self.target_port = 2222
        self.app = app
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client.settimeout(2)
        self.keep_connection_thread = True

    def keep_connection(self):
        while self.keep_connection_thread:
            self.create_and_send_packet(ACK + NONE + NO_FRAGMENT)
            sleep(5)

    def create_and_send_packet(self, msg):
        checksum = util.create_check_sum(msg)
        self.send(msg + checksum)

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
                    self.target_port = int(port)
                    break
                else:
                    print("[ERROR] Choose a valid port")

    def initialize(self):
        remaining_tries = 3
        self.choose_port_host()
        while True:
            try:
                self.create_and_send_packet(REQUEST + NONE + NO_FRAGMENT)
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
        self.create_and_send_packet(REQUEST + FAIL + NO_FRAGMENT)

    def no_frag_transfer(self, packet):
        while True:
            try:
                self.send(packet)
                msg, addr = self.client.recvfrom(PROTOCOL_SIZE)
                if msg[PACKET_TYPE_START:PACKET_TYPE_END] == ACK:
                    break
                else:
                    continue
            except TimeoutError:
                continue
        print('[INFO] Message was sent successfully')

    def send_created_packets(self, packets):
        for packet in packets:
            self.send(packet)

    def ack_sent_packets(self, packets):
        not_acked_packets = packets
        while True:
            try:
                msg, addr = self.client.recvfrom(PROTOCOL_SIZE)
                if msg[PACKET_TYPE_START:PACKET_TYPE_END] == ACK:
                    for packet in not_acked_packets:
                        if packet[FRAG_NUM_START:FRAG_NUM_END] == msg[FRAG_NUM_START:FRAG_NUM_END]:
                            not_acked_packets.remove(packet)
                        if not not_acked_packets:
                            return True
                elif msg[PACKET_TYPE_START:PACKET_TYPE_END] == REQUEST:
                    return False
            except TimeoutError:
                return False

    def frag_transfer(self, packets):
        not_acked_packets = packets
        msg_type = packets[0][MSG_TYPE_START:MSG_TYPE_END]
        while not_acked_packets:
            self.send_created_packets(not_acked_packets[:SLIDING_WINDOW_SIZE])
            if self.ack_sent_packets(not_acked_packets[:SLIDING_WINDOW_SIZE]):
                not_acked_packets = not_acked_packets[SLIDING_WINDOW_SIZE:]
            else:
                continue
        while True:
            try:
                self.create_and_send_packet(FIN + msg_type + util.create_frag_from_num(len(packets) + 1))
                msg, addr = self.client.recvfrom(PROTOCOL_SIZE)
                if msg[PACKET_TYPE_START:PACKET_TYPE_END] == ACK:
                    break
                continue
            except TimeoutError:
                continue
        if msg_type == TXT:
            print('[INFO] Message was sent successfully')
        else:
            print('[INFO] File was sent successfully')

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
                f"[INPUT] What will be the fragment size?(default/max = {PROTOCOL_SIZE} bytes,"
                f" lowest = {LOWEST_FRAGMENT_SIZE} bytes): ")
            if fragment_size == "":
                fragment_size = PROTOCOL_SIZE
                break
            if util.validate_fragment_size(fragment_size):
                break
            print("[ERROR] Choose a valid fragment size")
        if msg_type == 't':
            msg = input("[INPUT] Message you want to send: ")
            packets = PacketFactory.create_txt_packets(fragment_size, msg)
        else:
            while True:
                file_path = input("[INPUT] File path: ")
                if util.validate_file_path(file_path):
                    break
                print("[ERROR] Choose a valid file path")
            file_name = os.path.basename(file_path)
            packets = PacketFactory.create_file_packets(file_name, int(fragment_size))

        self.start_transfer(packets)
