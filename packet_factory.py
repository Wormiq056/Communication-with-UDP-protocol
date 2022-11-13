import zlib

from consts import HEADER_SIZE, TXT, FILE, DATA, NO_FRAGMENT, FORMAT, FRAG_NUM_LENGTH, CHECKSUM_LENGTH


class PacketFactory:
    def __init__(self, msg_type, fragment_size, msg=None, file_name=None):
        self.msg_type = msg_type
        self.fragment_size = fragment_size
        self.msg = msg
        self.file_name = file_name

    def create_frag_num(self, num):
        frag = num.to_bytes(FRAG_NUM_LENGTH, 'big')
        return frag

    def create_check_sum(self, msg):
        checksum = zlib.crc32(msg).to_bytes(CHECKSUM_LENGTH, 'big')
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
