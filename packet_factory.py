import zlib
import socket
from consts import HEADER_SIZE, PACKET_TYPE_START, PACKET_TYPE_END, ACK, FIN, REQUEST, DATA, \
    MSG_TYPE_START, MSG_TYPE_END, NONE, TXT, FILE, DATA, FRAG_NUM_START, FRAG_NUM_END, NO_FRAGMENT, CHECKSUM_START, \
    CHECKSUM_END, FAIL, PROTOCOL_SIZE, FORMAT


class PacketFactory:
    def __init__(self, msg_type, fragment_size, msg=None, file_name=None):
        self.msg_type = msg_type
        self.fragment_size = fragment_size
        self.msg = msg
        self.file_name = file_name

    def create_check_sum(self, msg):
        checksum = str(zlib.crc32(msg.encode(FORMAT)))
        while len(checksum) != 10:
            checksum = "0" + checksum
        return str(checksum)

    def create_frag_num(self, num):
        frag_num = str(num)
        while len(frag_num) != 5:
            frag_num = "0" + frag_num
        return frag_num

    def create_txt_packets(self):
        fragmented_packets = []
        if len(self.msg) > (int(self.fragment_size) - HEADER_SIZE):
            fragment_count = 1
            while self.msg:
                header = DATA + TXT + self.create_frag_num(fragment_count)
                txt_msg = self.msg[:int(self.fragment_size) - HEADER_SIZE]
                checksum = self.create_check_sum(header + txt_msg)
                fragmented_packets.append(header + checksum + txt_msg)
                fragment_count += 1
                self.msg = self.msg[int(self.fragment_size) - HEADER_SIZE:]

            return fragmented_packets
        else:
            header = DATA + TXT + NO_FRAGMENT
            txt_msg = self.msg
            checksum = self.create_check_sum(header + txt_msg)
            return header + checksum + txt_msg
