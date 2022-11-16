import collections
from time import sleep

from helpers import util
from helpers.consts import HEADER_SIZE, PACKET_TYPE_START, PACKET_TYPE_END, ACK, FIN, REQUEST, \
    MSG_TYPE_START, MSG_TYPE_END, NONE, TXT, FILE, DATA, FRAG_NUM_START, FRAG_NUM_END, NO_FRAGMENT, \
    FAIL, FORMAT, FIRST_FILE_PACKET, DOWNLOAD_PATH, SLIDING_WINDOW_SIZE


class ClientHandler:
    def __init__(self, addr, server):
        self.addr = addr
        self.server = server
        self.connection_time = 6
        self.file_name = ""
        self.num_of_incorrect_packets = 0
        self.go_back_n_dict = {}
        self.correct_fragments = 0
        self.total_num_of_packets_received = 0
        self.msg_byte_length = 0

    def reset_connection_time(self):
        self.connection_time = 6

    def hold_connection(self):
        while self.connection_time != 0 and self.server.running:
            if self.server.stopped():
                sleep(1)
                continue
            sleep(1)
            self.connection_time -= 1
        self.server.remove_connection(self.addr)

    def process_txt_packet(self, msg):
        if not util.compare_checksum(msg):
            print(f'[CLIENT] {self.addr} sent corrupted packet, sending error')
            self.num_of_incorrect_packets += 1
            self.total_num_of_packets_received += 1
            self.correct_fragments -= SLIDING_WINDOW_SIZE - 1
            self.create_and_send_response(REQUEST + FAIL + msg[FRAG_NUM_START:FRAG_NUM_END])
            return

        if msg[FRAG_NUM_START:FRAG_NUM_END] != NO_FRAGMENT:
            self.correct_fragments += 1
            self.total_num_of_packets_received += 1
            print(f'[CLIENT] {self.addr} fragment {int.from_bytes(msg[FRAG_NUM_START:FRAG_NUM_END], "big")} recieved')
            self.go_back_n_dict[int.from_bytes(msg[FRAG_NUM_START:FRAG_NUM_END], 'big')] = msg[HEADER_SIZE:]
            self.create_and_send_response(ACK + NONE + msg[FRAG_NUM_START:FRAG_NUM_END])
        else:
            self.total_num_of_packets_received += 1
            self.correct_fragments += 1
            print(f"[CLIENT] Message from {self.addr} client: " + msg[HEADER_SIZE:].decode(FORMAT))
            self.create_and_send_response(ACK + NONE + NO_FRAGMENT)
            self.msg_byte_length += int.from_bytes(msg[HEADER_SIZE:], "big")
            self.transmission_statistics()

    def process_file_packet(self, msg):
        if not util.compare_checksum(msg):
            self.num_of_incorrect_packets += 1
            self.total_num_of_packets_received += 1
            self.correct_fragments -= SLIDING_WINDOW_SIZE - 1
            print(f'[CLIENT] {self.addr} sent corrupted packet, sending error')
            self.create_and_send_response(REQUEST + FAIL + msg[FRAG_NUM_START:FRAG_NUM_END])
            return

        if msg[FRAG_NUM_START:FRAG_NUM_END] == FIRST_FILE_PACKET:
            print(f'[CLIENT] {self.addr} fragment {int.from_bytes(msg[FRAG_NUM_START:FRAG_NUM_END], "big")} recieved')
            self.file_name = DOWNLOAD_PATH + msg[HEADER_SIZE:].decode(FORMAT)
            self.create_and_send_response(ACK + NONE + msg[FRAG_NUM_START:FRAG_NUM_END])
            self.total_num_of_packets_received += 1
            self.correct_fragments += 1
        else:
            print(f'[CLIENT] {self.addr} fragment {int.from_bytes(msg[FRAG_NUM_START:FRAG_NUM_END], "big")} recieved')
            self.go_back_n_dict[int.from_bytes(msg[FRAG_NUM_START:FRAG_NUM_END], 'big')] = msg[HEADER_SIZE:]
            self.create_and_send_response(ACK + NONE + msg[FRAG_NUM_START:FRAG_NUM_END])
            self.total_num_of_packets_received += 1
            self.correct_fragments += 1

    def process_data_packet(self, msg):
        if msg[MSG_TYPE_START:MSG_TYPE_END] == TXT:
            self.process_txt_packet(msg)
        elif msg[MSG_TYPE_START:MSG_TYPE_END] == FILE:
            self.process_file_packet(msg)

    def create_and_send_response(self, response):
        checksum = util.create_check_sum(response)
        self.server.send(response + checksum, self.addr)

    def process_fin(self, msg):
        if not util.compare_checksum(msg):
            print(f'[CLIENT] {self.addr} sent corrupted packet, sending error')
            self.create_and_send_response(REQUEST + FAIL + msg[FRAG_NUM_START:FRAG_NUM_END])
            return
        self.create_and_send_response(ACK + NONE + msg[FRAG_NUM_START:FRAG_NUM_END])
        if msg[MSG_TYPE_START:MSG_TYPE_END] == TXT:
            ordered_msg = collections.OrderedDict(sorted(self.go_back_n_dict.items()))
            client_msg = ""
            for key, value in ordered_msg.items():
                self.msg_byte_length += len(value)
                client_msg = client_msg + value.decode(FORMAT)
            print(f"[CLIENT] Message from {self.addr} client: " + client_msg)

        elif msg[MSG_TYPE_START:MSG_TYPE_END] == FILE:
            self.dump_file()
            print(f"[CLIENT] File was successfully downloaded and saved to : {self.file_name}")
            self.file_name = ""

        self.go_back_n_dict.clear()
        self.transmission_statistics()

    def dump_file(self):
        sorted_dict = collections.OrderedDict(sorted(self.go_back_n_dict.items()))
        with open(self.file_name, 'wb') as file:
            for value in sorted_dict.values():
                self.msg_byte_length += len(value)
                file.write(value)
        self.go_back_n_dict.clear()

    def transmission_statistics(self):
        print(f"[STATISTICS] Received message raw byte length {self.msg_byte_length} bytes")
        print(f"[STATISTICS] Number of total packets received {self.total_num_of_packets_received}")
        print(f"[STATISTICS] Number of correct packets received {self.correct_fragments}")
        print(f"[STATISTICS] Number of incorrect packets sent {self.num_of_incorrect_packets}")

        self.msg_byte_length = 0
        self.correct_fragments = 0
        self.total_num_of_packets_received = 0
        self.num_of_incorrect_packets = 0

    def process_packet(self, msg):
        self.reset_connection_time()
        if msg[PACKET_TYPE_START:PACKET_TYPE_END] == DATA:
            self.process_data_packet(msg)
        elif msg[PACKET_TYPE_START:PACKET_TYPE_END] == FIN:
            self.process_fin(msg)
        elif msg[PACKET_TYPE_START:PACKET_TYPE_END] == REQUEST:
            if msg[MSG_TYPE_START:MSG_TYPE_END] == FAIL:
                self.server.remove_connection(self.addr)
            elif msg[MSG_TYPE_START:MSG_TYPE_END] == NONE:
                self.create_and_send_response(ACK + NONE + NO_FRAGMENT)
