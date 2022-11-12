import zlib
from consts import HEADER, PACKET_TYPE_START, PACKET_TYPE_END, ACK, FIN, REQUEST, \
    MSG_TYPE_START, MSG_TYPE_END, NONE, TXT, FILE, DATA, FRAG_NUM_START, FRAG_NUM_END, NO_FRAGMENT, CHECKSUM_START, \
    CHECKSUM_END, FAIL
from time import sleep


class ClientHandler:
    def __init__(self, addr, server):
        self.addr = addr
        self.server = server
        self.connection_time = 5
        self.next_fragment = 1
        self.current_txt_msg = []

    def reset_connection_time(self):
        self.connection_time = 5

    def hold_connection(self):
        while self.connection_time != 0:
            sleep(1)
            self.connection_time -= 1
        self.server.remove_connection(self.addr)

    def compare_checksum(self, msg):
        sent_checksum = int(msg[CHECKSUM_START:CHECKSUM_END])
        if zlib.crc32(bytes(msg)) != sent_checksum:
            return False
        return True

    def create_frag_num(self):
        frag = str(self.next_fragment)
        while len(frag) != 5:
            frag = "0" + frag
        return frag

    def create_check_sum(self, msg):
        checksum = zlib.crc32(bytes(msg))
        return str(checksum)

    def check_frag_number(self, msg):
        if msg[FRAG_NUM_START:FRAG_NUM_END] == NO_FRAGMENT:
            return True
        if int(msg[FRAG_NUM_START:FRAG_NUM_END]) != self.current_txt_msg:
            return False
        return True

    def process_txt_packet(self, msg):
        if not self.compare_checksum(msg):
            response = REQUEST + FAIL + self.create_frag_num()
            checksum = self.create_check_sum(response)
            self.server.send(response + checksum, self.addr)
            return
        if not self.check_frag_number(msg):
            response = REQUEST + FAIL + self.create_frag_num()
            checksum = self.create_check_sum(response)
            self.server.send(response + checksum, self.addr)
            return
        if msg[FRAG_NUM_START:FRAG_NUM_END] != NO_FRAGMENT:
            print(f'{self.addr}] fragment {self.next_fragment} recieved')
            self.current_txt_msg.append(msg[HEADER:])
            self.next_fragment += 1
            response = ACK + NONE + self.create_frag_num()
            checksum = self.create_check_sum(response)
            self.server.send(response + checksum, self.addr)
        else:
            print(msg[HEADER:])
            response = ACK + NONE + NO_FRAGMENT
            checksum = self.create_check_sum(response)
            self.server.send(response + checksum, self.addr)

    def process_data_packet(self, msg):
        if msg[MSG_TYPE_START:MSG_TYPE_END] == TXT:
            self.process_txt_packet(msg)
        elif msg[MSG_TYPE_START:MSG_TYPE_END] == FILE:
            pass

    def process_fin(self, msg):
        if msg[MSG_TYPE_START:MSG_TYPE_END] == TXT:
            if not self.check_frag_number(msg):
                response = REQUEST + FAIL + self.create_frag_num()
                checksum = self.create_check_sum(response)
                self.server.send(response + checksum, self.addr)
                return
            self.next_fragment = 0
            print("".join(self.current_txt_msg))
            self.current_txt_msg = []

    def process_msg(self, msg):
        self.reset_connection_time()
        if msg[PACKET_TYPE_START:PACKET_TYPE_END] == DATA:
            self.process_data_packet(msg)
        elif msg[PACKET_TYPE_START:PACKET_TYPE_END] == FIN:
            self.process_fin(msg)
        elif msg[PACKET_TYPE_START:PACKET_TYPE_END] == REQUEST:
            if msg[MSG_TYPE_START:MSG_TYPE_END] == FAIL:
                self.server.remove_connection(self.addr)
            elif msg[MSG_TYPE_START:MSG_TYPE_END] == NONE:
                response = REQUEST + FAIL + NO_FRAGMENT
                checksum = self.create_check_sum(response)
                self.server.send(response + checksum, self.addr)
        elif msg[PACKET_TYPE_START:PACKET_TYPE_END] == ACK:
            self.reset_connection_time()
