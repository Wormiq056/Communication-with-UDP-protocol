import zlib
import socket
from consts import HEADER_SIZE, PACKET_TYPE_START, PACKET_TYPE_END, ACK, FIN, REQUEST, DATA, \
    MSG_TYPE_START, MSG_TYPE_END, NONE, TXT, FILE, DATA, FRAG_NUM_START, FRAG_NUM_END, NO_FRAGMENT, CHECKSUM_START, \
    CHECKSUM_END, FAIL, PROTOCOL_SIZE, FORMAT
import os


class PacketFactory:
    def __init__(self, msg_type, fragment_size, msg=None, file_name=None):
        self.msg_type = msg_type
        self.fragment_size = fragment_size
        self.msg = msg
        self.file_name = file_name


    def create_frag_num(self,num):
        frag = num.to_bytes(6, 'big')
        # while len(frag) != 6:
        #     frag = "0" + frag
        return frag

    def create_check_sum(self, msg):
        checksum = zlib.crc32(msg).to_bytes(4,'big')
        # while len(checksum) != 10:
        #     checksum = "0" + checksum
        return checksum



    def create_txt_packets(self):
        fragmented_packets = []
        if len(self.msg) > (int(self.fragment_size) - int(HEADER_SIZE)):
            fragment_count = 1
            while self.msg:
                header = DATA + TXT + self.create_frag_num(fragment_count)
                txt_msg = self.msg[:int(self.fragment_size) - int(HEADER_SIZE)].encode(FORMAT)
                checksum = self.create_check_sum(header + txt_msg)
                fragmented_packets.append(header + checksum + txt_msg)
                fragment_count += 1
                self.msg = self.msg[int(self.fragment_size) - int(HEADER_SIZE):]

            return fragmented_packets
        else:
            header = DATA + TXT + NO_FRAGMENT
            txt_msg = self.msg.encode(FORMAT)
            checksum = self.create_check_sum(header + txt_msg)
            return header + checksum + txt_msg

    def create_file_packets(self):
        file_size = os.stat(self.file_name).st_size
        first_header = DATA + FILE + self.create_frag_num(1)
        packet_msg = self.file_name.encode(FORMAT)
        checksum = self.create_check_sum(first_header + packet_msg)
        fragmented_packets = [first_header + checksum + packet_msg]
        buffer = (self.fragment_size - HEADER_SIZE)
        fragment_count = 2
        with open(self.file_name, 'rb') as file:
            while True:
                data = file.read(buffer)
                if not data:
                    break
                packet_header = DATA + FILE + self.create_frag_num(fragment_count)
                fragment_count += 1
                checksum = self.create_check_sum(packet_header + data)
                fragmented_packets.append(packet_header + checksum + data)

        return fragmented_packets
