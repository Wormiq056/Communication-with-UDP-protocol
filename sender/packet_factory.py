from helpers import util
from helpers.consts import HEADER_SIZE, TXT, FILE, DATA, NO_FRAGMENT, FORMAT


class PacketFactory:
    @staticmethod
    def create_txt_packets(fragment_size, msg):
        fragmented_packets = []
        if len(msg) > (int(fragment_size) - int(HEADER_SIZE)):
            fragment_count = 1
            while msg:
                header = DATA + TXT + util.create_frag_from_num(fragment_count)
                txt_msg = msg[:int(fragment_size) - int(HEADER_SIZE)].encode(FORMAT)
                checksum = util.create_check_sum(header + txt_msg)
                fragmented_packets.append(header + checksum + txt_msg)
                fragment_count += 1
                msg = msg[int(fragment_size) - int(HEADER_SIZE):]

            return fragmented_packets
        else:
            header = DATA + TXT + NO_FRAGMENT
            txt_msg = msg.encode(FORMAT)
            checksum = util.create_check_sum(header + txt_msg)
            return header + checksum + txt_msg

    @staticmethod
    def create_file_packets(file_name, fragment_size):
        first_header = DATA + FILE + util.create_frag_from_num(1)
        packet_msg = file_name.encode(FORMAT)
        checksum = util.create_check_sum(first_header + packet_msg)
        fragmented_packets = [first_header + checksum + packet_msg]
        buffer = (fragment_size - HEADER_SIZE)
        fragment_count = 2
        with open(file_name, 'rb') as file:
            while True:
                data = file.read(buffer)
                if not data:
                    break
                packet_header = DATA + FILE + util.create_frag_from_num(fragment_count)
                fragment_count += 1
                checksum = util.create_check_sum(packet_header + data)
                fragmented_packets.append(packet_header + checksum + data)

        return fragmented_packets
