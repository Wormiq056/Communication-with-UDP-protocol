import zlib
from time import sleep

from helpers.consts import HEADER_SIZE, PACKET_TYPE_START, PACKET_TYPE_END, ACK, FIN, REQUEST, \
    MSG_TYPE_START, MSG_TYPE_END, NONE, TXT, FILE, DATA, FRAG_NUM_START, FRAG_NUM_END, NO_FRAGMENT, CHECKSUM_START, \
    CHECKSUM_END, FAIL, FORMAT, FIRST_FILE_PACKET, DOWNLOAD_PATH


class ClientHandler:
    def __init__(self, addr, server):
        self.addr = addr
        self.server = server
        self.connection_time = 6
        self.next_fragment = 1
        self.current_txt_msg = []
        self.transfered_file_name = ""
        self.transfer_file_pointer = None
        self.num_of_incorrect_packets = 0

    def reset_connection_time(self):
        self.connection_time = 6

    def hold_connection(self):
        while self.connection_time != 0:
            sleep(1)
            self.connection_time -= 1
        self.server.remove_connection(self.addr)

    def compare_checksum(self, msg):
        sent_checksum = msg[CHECKSUM_START:CHECKSUM_END]
        server_checksum = msg[:CHECKSUM_START] + msg[CHECKSUM_END:]
        if zlib.crc32(server_checksum).to_bytes(4, 'big') != sent_checksum:
            return False
        return True

    def create_frag_num(self):
        frag = self.next_fragment.to_bytes(6, 'big')
        return frag

    def create_check_sum(self, msg):
        checksum = zlib.crc32(msg).to_bytes(4, 'big')
        return checksum

    def check_frag_number(self, msg):
        if msg[FRAG_NUM_START:FRAG_NUM_END] == NO_FRAGMENT:
            return True
        if msg[FRAG_NUM_START:FRAG_NUM_END] != self.next_fragment.to_bytes(6, 'big'):
            return False
        return True

    def process_txt_packet(self, msg):
        if not self.compare_checksum(msg):
            print(f'[CLIENT] {self.addr} sent corrupted packet, sending error')
            self.num_of_incorrect_packets += 1
            response = REQUEST + FAIL + self.create_frag_num()
            checksum = self.create_check_sum(response)
            self.server.send(response + checksum, self.addr)
            return
        if not self.check_frag_number(msg):
            print(f'[CLIENT] {self.addr} sent incorrect fragment, sending error')
            self.num_of_incorrect_packets += 1
            response = REQUEST + FAIL + self.create_frag_num()
            checksum = self.create_check_sum(response)
            self.server.send(response + checksum, self.addr)
            return
        if msg[FRAG_NUM_START:FRAG_NUM_END] != NO_FRAGMENT:
            print(f'[CLIENT] {self.addr}] fragment {self.next_fragment} recieved')
            self.current_txt_msg.append(msg[HEADER_SIZE:].decode(FORMAT))
            self.next_fragment += 1
            response = ACK + NONE + self.create_frag_num()
            checksum = self.create_check_sum(response)
            self.server.send(response + checksum, self.addr)
        else:
            print(f"[CLIENT] Message from {self.addr} client: " + msg[HEADER_SIZE:].decode(FORMAT))
            response = ACK + NONE + NO_FRAGMENT
            checksum = self.create_check_sum(response)
            self.server.send(response + checksum, self.addr)

    def process_file_packet(self, msg):
        if not self.compare_checksum(msg):
            self.num_of_incorrect_packets += 1
            print(f'[CLIENT] {self.addr} sent corrupted packet, sending error')
            response = REQUEST + FAIL + self.create_frag_num()
            checksum = self.create_check_sum(response)
            self.server.send(response + checksum, self.addr)
            return
        if not self.check_frag_number(msg):
            self.num_of_incorrect_packets += 1
            print(f'[CLIENT] {self.addr} sent incorrect fragment, sending error')
            response = REQUEST + FAIL + self.create_frag_num()
            checksum = self.create_check_sum(response)
            self.server.send(response + checksum, self.addr)
            return
        if msg[FRAG_NUM_START:FRAG_NUM_END] == FIRST_FILE_PACKET:
            print(f'[CLIENT] {self.addr}] fragment {self.next_fragment} recieved')
            self.transfered_file_name = DOWNLOAD_PATH + msg[HEADER_SIZE:].decode(FORMAT)
            self.next_fragment += 1
            self.transfer_file_pointer = open(self.transfered_file_name, 'wb')
            response = ACK + NONE + self.create_frag_num()
            checksum = self.create_check_sum(response)
            self.server.send(response + checksum, self.addr)
        else:
            print(f'[CLIENT] {self.addr}] fragment {self.next_fragment} recieved')
            self.next_fragment += 1
            file_data = msg[HEADER_SIZE:]
            self.transfer_file_pointer.write(file_data)
            response = ACK + NONE + self.create_frag_num()
            checksum = self.create_check_sum(response)
            self.server.send(response + checksum, self.addr)

    def process_data_packet(self, msg):
        if msg[MSG_TYPE_START:MSG_TYPE_END] == TXT:
            self.process_txt_packet(msg)
        elif msg[MSG_TYPE_START:MSG_TYPE_END] == FILE:
            self.process_file_packet(msg)

    def process_fin(self, msg):

        if msg[MSG_TYPE_START:MSG_TYPE_END] == TXT:
            if not self.check_frag_number(msg):
                response = REQUEST + FAIL + self.create_frag_num()
                checksum = self.create_check_sum(response)
                self.server.send(response + checksum, self.addr)
                return
            response = ACK + NONE + self.create_frag_num()
            checksum = self.create_check_sum(response)
            self.server.send(response + checksum, self.addr)
            if msg[FRAG_NUM_START:FRAG_NUM_END] != NO_FRAGMENT:
                print(f"[CLIENT] Message from {self.addr} client: " + "".join(self.current_txt_msg))
            self.current_txt_msg = []
        elif msg[MSG_TYPE_START:MSG_TYPE_END] == FILE:
            if not self.check_frag_number(msg):
                response = REQUEST + FAIL + self.create_frag_num()
                checksum = self.create_check_sum(response)
                self.server.send(response + checksum, self.addr)
                return
            response = ACK + NONE + self.create_frag_num()
            checksum = self.create_check_sum(response)
            self.server.send(response + checksum, self.addr)
            print(f"[CLIENT] File was successfully downloaded and saved to : {self.transfered_file_name}")
            self.transfer_file_pointer.close()
            self.transfered_file_name = None
        self.transmission_statistics()

    def transmission_statistics(self):
        print(f"[STATISTIC] Number of correctly received packets {self.next_fragment}")
        print(f"[STATISTIC] Number of incorrect packets received {self.num_of_incorrect_packets}")
        self.next_fragment = 1

    def process_packet(self, msg):
        if msg[PACKET_TYPE_START:PACKET_TYPE_END] == DATA:
            self.process_data_packet(msg)
        elif msg[PACKET_TYPE_START:PACKET_TYPE_END] == FIN:
            self.process_fin(msg)
        elif msg[PACKET_TYPE_START:PACKET_TYPE_END] == REQUEST:
            if msg[MSG_TYPE_START:MSG_TYPE_END] == FAIL:
                self.server.remove_connection(self.addr)
            elif msg[MSG_TYPE_START:MSG_TYPE_END] == NONE:
                response = ACK + NONE + NO_FRAGMENT
                checksum = self.create_check_sum(response)
                self.server.send(response + checksum, self.addr)
        elif msg[PACKET_TYPE_START:PACKET_TYPE_END] == ACK:
            self.reset_connection_time()
