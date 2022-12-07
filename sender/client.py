import random
import socket
from threading import Thread
from time import sleep
from typing import List

from helpers import util
from helpers.consts import PACKET_TYPE_START, PACKET_TYPE_END, ACK, FIN, REQUEST, MSG_TYPE_START, MSG_TYPE_END, NONE, \
    NO_FRAGMENT, FAIL, PROTOCOL_SIZE, LOWEST_FRAGMENT_SIZE, TXT, FRAG_NUM_START, FRAG_NUM_END, \
    NO_CHECKSUM, DATA, FILE, SIMULATION_FILE_PATH, HEADER_SIZE, SIMULATION_FILE_FRAGMENT_SIZE
from sender.packet_factory import PacketFactory


class Client:
    """
    class that acts as a client when we want to send a msg/file, it ensures correct packet transmission
    """
    connection_thread: Thread

    def __init__(self, program_interface) -> None:
        self.target_host = "127.0.0.1"
        self.target_port = 2222
        self.program_interface = program_interface
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client.settimeout(2)
        self.keep_connection_thread = False
        self.total_number_of_packets_send = 0
        self.number_of_incorrect_packets_send = 0
        self.msg_packet_length = 0
        self.msg_byte_length = 0

    def keep_connection(self) -> None:
        """
        method that sends packet every 5 seconds to keep connection to the server,
        it runs on a separate thread
        """
        while self.keep_connection_thread:
            self.create_and_send_packet(ACK + NONE + NO_FRAGMENT + NO_CHECKSUM)
            sleep(5)

    def create_and_send_packet(self, msg: bytes) -> None:
        """
        helper method that calculates checksum of packet, these packets will not be DATA packets
        :param msg: packet we want to send
        """
        checksum = util.create_check_sum(msg)
        self.send(msg + checksum)

    def choose_port_host(self) -> None:
        """
        method that corrects that is used to choose to which IP and port we want to send something, it also checks
        validity of input
        """
        while True:
            host = (input("[INPUT] Choose receiver host(default 127.0.0.1): "))
            if host == "":
                break
            else:
                if util.validate_ip_address(host):
                    self.target_host = host
                    break
                else:
                    print("[ERROR] Choose a valid IP address")
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

    def initialize(self) -> None:
        """
        method that is called when we want to connect to a server or when we are already connected it checks is server
        is still online
        """
        remaining_tries = 3
        if not self.keep_connection_thread:
            self.choose_port_host()
        while True:
            try:
                self.create_and_send_packet(REQUEST + NONE + NO_FRAGMENT)
                msg, addr = self.client.recvfrom(PROTOCOL_SIZE)
                if msg[PACKET_TYPE_START:PACKET_TYPE_END] != ACK:
                    print(msg[PACKET_TYPE_START:PACKET_TYPE_END])
                    if remaining_tries <= 0:
                        print(f'[CONNECTION] {self.target_host} is unreachable')
                        self.keep_connection_thread = False
                        return
                    remaining_tries -= 1
                    print(f'[CONNECTION] Connection to {self.target_host} failed, remaining tries {remaining_tries}')
                    continue
                break
            except ConnectionResetError:
                if remaining_tries <= 0:
                    self.keep_connection_thread = False
                    print(f'[CONNECTION] {self.target_host} is unreachable')
                    self.program_interface.connection_error()
                    return
                remaining_tries -= 1
                print(f'[CONNECTION] Connection to {self.target_host} failed, remaining tries {remaining_tries}')
                continue
            except TimeoutError:
                if remaining_tries <= 0:
                    self.keep_connection_thread = False
                    print(f'[CONNECTION] {self.target_host} is unreachable')
                    self.program_interface.connection_error()
                    return
                remaining_tries -= 1
                print(f'[CONNECTION] Connection to {self.target_host} failed, remaining tries {remaining_tries}')
                continue
        if not self.keep_connection_thread:
            self.keep_connection_thread = True
            print(f'[CONNECTION] Connection to {self.target_host} established')
            self.connection_thread = Thread(target=self.keep_connection)
            self.connection_thread.start()
        self.create_msg()

    def send(self, msg: bytes) -> None:
        """
        method that sends given packet to server
        :param msg: packet we want to send
        """
        self.client.sendto(msg, (self.target_host, self.target_port))

    def close(self) -> None:
        """
        method that is called when we want to close connection to the server
        """
        self.keep_connection_thread = False
        if self.connection_thread.is_alive():
            print(f"[INFO] Closing connection to {self.target_host, self.target_port}")
            self.connection_thread.join()
        self.create_and_send_packet(REQUEST + FAIL + NO_FRAGMENT)

    def no_frag_transfer(self, packet) -> None:
        """
        method that is called when message we want to send is not fragmented
        :param packet: packet we want to send
        """
        remaining_tries = 3

        while True:
            try:
                self.total_number_of_packets_send += 1
                self.send(packet)
                msg, addr = self.client.recvfrom(PROTOCOL_SIZE)
                if not util.compare_checksum(msg):
                    print("[ERROR] Server sent corrupted packet, resending packets")
                if msg[PACKET_TYPE_START:PACKET_TYPE_END] == ACK:
                    if msg[FRAG_NUM_START:FRAG_NUM_END] == packet[FRAG_NUM_START:FRAG_NUM_END]:
                        remaining_tries = 3
                        break
                else:
                    self.number_of_incorrect_packets_send += 1
                    print("[ERROR] Server received corrupted packet, resending packets")
                    continue
            except TimeoutError:
                if remaining_tries <= 0:
                    self.keep_connection_thread = False
                    print(f'[ERROR] {self.target_host} is unreachable')
                    self.program_interface.connection_error()
                    return
                remaining_tries -= 1
                print("[ERROR] Server did not ACK packet resending packet")
                print(f"[ERROR] Remaining tries {remaining_tries}")
                continue
        self.transfer_statistics()
        print('[INFO] Message was sent successfully')

    def frag_transfer(self, packets: List[bytes]) -> None:
        """
        method that is called when wa want to send fragmented msg, it implements stop & wait ARQ method,
        meaning we send one packet and wait for it's ACK if ACK is not received we sent it again
        :param packets: packets we want to send
        """
        remaining_tries = 3

        msg_type: bytes = packets[0][MSG_TYPE_START:MSG_TYPE_END]
        for packet in packets:
            while True:
                try:
                    self.send(packet)
                    self.total_number_of_packets_send += 1
                    msg, addr = self.client.recvfrom(PROTOCOL_SIZE)
                    if not util.compare_checksum(msg):
                        print("[ERROR] Server sent corrupted packet, resending packet")
                    if msg[PACKET_TYPE_START:PACKET_TYPE_END] == ACK:
                        if msg[FRAG_NUM_START:FRAG_NUM_END] == packet[FRAG_NUM_START:FRAG_NUM_END]:
                            remaining_tries = 3
                            break
                    print('[ERROR] Server received corrupted packet, resending packet')
                    self.number_of_incorrect_packets_send += 1
                except TimeoutError:
                    if remaining_tries <= 0:
                        self.keep_connection_thread = False
                        print(f'[ERROR] {self.target_host} has been timed out')
                        self.program_interface.connection_error()
                        return
                    remaining_tries -= 1
                    print("[ERROR] Server did not ACK packet resending packet")
                    print(f"[ERROR] Remaining tries {remaining_tries}")
                    continue

        remaining_tries = 3
        while True:
            try:
                self.create_and_send_packet(FIN + msg_type + util.create_frag_from_num(len(packets) + 1))
                msg, addr = self.client.recvfrom(PROTOCOL_SIZE)
                if not util.compare_checksum(msg):
                    print("[ERROR] Server sent corrupted packet, resending finalizing packet")
                if msg[PACKET_TYPE_START:PACKET_TYPE_END] == ACK:
                    break
                else:
                    print("[ERROR] Server received corrupted packet, resending finalizing packet")
                continue
            except TimeoutError:
                if remaining_tries <= 0:
                    self.keep_connection_thread = False
                    print(f'[ERROR] {self.target_host} has been timed out')
                    self.program_interface.connection_error()
                    return
                remaining_tries -= 1
                print("[ERROR] Server did not ACK packet resending packet")
                print(f"[ERROR] Remaining tries {remaining_tries}")
                continue

        self.transfer_statistics()
        if msg_type == TXT:
            print('[INFO] Message was sent successfully')
        else:
            print('[INFO] File was sent successfully')

    def transfer_statistics(self) -> None:
        """
        method that is called after message was sent successfully, it display transfer statistics
        """
        print(f"[STATISTICS] Message raw byte length {self.msg_byte_length} bytes")
        print(f"[STATISTICS] Packets needed for message transfer {self.msg_packet_length}")
        print(f"[STATISTICS] Number of total packets sent {self.total_number_of_packets_send}")
        print(f"[STATISTICS] Number of incorrect packets sent {self.number_of_incorrect_packets_send}")
        self.msg_byte_length = 0
        self.msg_packet_length = 0
        self.total_number_of_packets_send = 0
        self.number_of_incorrect_packets_send = 0

    def calculate_bytes_of_msg(self, packets) -> None:
        """
        method that calculates size in bytes of msg/file we want to send
        :param packets: message wa want to calculate
        """
        for packet in packets:
            self.msg_byte_length += len(packet) - HEADER_SIZE

    def start_transfer(self, packets) -> None:
        """
        method that chooses which transfer method based on message fragmentation
        :param packets: packet/s we want to transfer
        """
        if isinstance(packets, bytes):
            self.msg_packet_length = 1
            self.msg_byte_length += len(packets) - HEADER_SIZE
            self.no_frag_transfer(packets)
        elif isinstance(packets, list):
            self.msg_packet_length = len(packets)
            self.calculate_bytes_of_msg(packets)
            self.frag_transfer(packets)

    def create_msg(self) -> None:
        """
        method that takes inputs from terminal with validation for message transfer
        """
        while True:
            msg_type = input("[INPUT] What type of message, file or text?(f/t): ")
            if util.validate_msg_type(msg_type):
                break
            print("[ERROR] Choose a valid message type")
        while True:
            fragment_size = input(
                f"[INPUT] What will be the fragment size?(default/max = {PROTOCOL_SIZE - HEADER_SIZE} bytes,"
                f" lowest = {LOWEST_FRAGMENT_SIZE} bytes): ") + HEADER_SIZE
            if fragment_size == "":
                fragment_size = PROTOCOL_SIZE
                break
            if util.validate_fragment_size(fragment_size):
                break
            print("[ERROR] Choose a valid fragment size")
        if msg_type == 't':
            msg = input("[INPUT] Message you want to send: ")
            if msg == "":
                self.simulate_error(TXT)
            else:
                packets = PacketFactory.create_txt_packets(fragment_size, msg)
                self.start_transfer(packets)
        else:
            while True:
                file_path = input("[INPUT] File path: ")
                if util.validate_file_path(file_path):
                    break
                print("[ERROR] Choose a valid file path")
            if file_path == "":
                self.simulate_error(FILE)
            else:
                packets = PacketFactory.create_file_packets(file_path, int(fragment_size))
                self.start_transfer(packets)

    def simulate_error(self, test_type: bytes) -> None:
        """
        method is called when wa want to simulate error in packet transfer
        :param test_type: TXT or FILE
        """
        if test_type == TXT:
            print(f"[SIMULATION] Starting simulation for TXT message with corrupted packet")
            generated_msg, packets = PacketFactory.create_simulation_txt_packets()
            print(f'[SIMULATION] Generated message: {generated_msg}')
        else:
            print(f"[SIMULATION] Starting simulation for FILE transfer with corrupted packet")
            packets = PacketFactory.create_file_packets(SIMULATION_FILE_PATH, SIMULATION_FILE_FRAGMENT_SIZE)
            print(f"[SIMULATION] Sending {SIMULATION_FILE_PATH} to the server")
        self.error_simulation(packets)

    def error_simulation(self, packets: List[bytes]) -> None:
        """
        method that is called when we simulate error transfer
        :param packets: packets we want to transfer
        """
        self.msg_packet_length = len(packets)
        self.calculate_bytes_of_msg(packets)
        msg_type: bytes = packets[0][MSG_TYPE_START:MSG_TYPE_END]
        remaining_tries = 1
        random_num = random.randint(0, len(packets) - 1)
        random_packet = packets[random_num]
        test_packets = packets.copy()
        test_packets[random_num] = DATA + msg_type + util.create_frag_from_num(random_num + 1) + NO_CHECKSUM
        remaining_timeout = 3
        for packet in test_packets:
            while True:
                try:
                    if remaining_tries == 0:
                        remaining_tries -= 1
                        packet = random_packet
                    self.send(packet)
                    self.total_number_of_packets_send += 1
                    msg, addr = self.client.recvfrom(PROTOCOL_SIZE)
                    if not util.compare_checksum(msg):
                        print("[ERROR] Server sent corrupted packet, resending packet")
                        continue
                    if msg[PACKET_TYPE_START:PACKET_TYPE_END] == ACK:
                        if msg[FRAG_NUM_START:FRAG_NUM_END] == packet[FRAG_NUM_START:FRAG_NUM_END]:
                            break
                    remaining_tries -= 1
                    print('[ERROR] Server received corrupted packet, resending packet')
                    self.number_of_incorrect_packets_send += 1

                except TimeoutError:
                    if remaining_timeout <= 0:
                        self.keep_connection_thread = False
                        print(f'[ERROR] {self.target_host} has been timed out')
                        self.program_interface.connection_error()
                        return
                    remaining_timeout -= 1
                    print("[ERROR] Server did not ACK packet resending packet")
                    print(f"[ERROR] Remaining tries {remaining_tries}")
                    continue

        while True:
            try:
                self.create_and_send_packet(FIN + msg_type + util.create_frag_from_num(len(packets) + 1))
                msg, addr = self.client.recvfrom(PROTOCOL_SIZE)
                if not util.compare_checksum(msg):
                    print("[ERROR] Server sent corrupted packet, resending finalizing packet")
                if msg[PACKET_TYPE_START:PACKET_TYPE_END] == ACK:
                    break
                else:
                    print("[ERROR] Server received corrupted packet, resending finalizing packet")
                continue
            except TimeoutError:
                continue

        self.transfer_statistics()
        if msg_type == TXT:
            print('[SIMULATION] Message was sent successfully')
        else:
            print('[SIMULATION] File was sent successfully')
