import random
import string
import os
from helpers import util
from helpers.consts import HEADER_SIZE, TXT, FILE, DATA, NO_FRAGMENT, FORMAT, TEST_TXT_NUM_OF_PACKETS, \
    TEST_TXT_FRAGMENT_SIZE, TEST_FILE_FRAGMENT_SIZE, TEST_FILE_PATH


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
    def create_file_packets(file_path, fragment_size):
        first_header = DATA + FILE + util.create_frag_from_num(1)
        packet_msg = os.path.basename(file_path).encode(FORMAT)
        checksum = util.create_check_sum(first_header + packet_msg)
        fragmented_packets = [first_header + checksum + packet_msg]
        buffer = (fragment_size - HEADER_SIZE)
        fragment_count = 2
        with open(file_path, 'rb') as file:
            while True:
                data = file.read(buffer)
                if not data:
                    break
                packet_header = DATA + FILE + util.create_frag_from_num(fragment_count)
                fragment_count += 1
                checksum = util.create_check_sum(packet_header + data)
                fragmented_packets.append(packet_header + checksum + data)

        return fragmented_packets

    @staticmethod
    def create_test_txt_packets():
        test_packets = []

        for i in range(TEST_TXT_NUM_OF_PACKETS):
            msg = ''.join(
                random.choices(string.ascii_uppercase + string.digits, k=TEST_TXT_FRAGMENT_SIZE - HEADER_SIZE)).encode(
                FORMAT)
            packet_header = DATA + TXT + util.create_frag_from_num(i + 1)
            checksum = util.create_check_sum(packet_header + msg)
            test_packets.append(packet_header + checksum + msg)

        return test_packets

    @staticmethod
    def create_test_file_packets():
        first_header = DATA + FILE + util.create_frag_from_num(1)
        packet_msg = os.path.basename(TEST_FILE_PATH).encode(FORMAT)
        checksum = util.create_check_sum(first_header + packet_msg)
        fragmented_packets = [first_header + checksum + packet_msg]
        buffer = (TEST_FILE_FRAGMENT_SIZE - HEADER_SIZE)
        fragment_count = 2
        with open(TEST_FILE_PATH, 'rb') as file:
            while True:
                data = file.read(buffer)
                if not data:
                    break
                packet_header = DATA + FILE + util.create_frag_from_num(fragment_count)
                fragment_count += 1
                checksum = util.create_check_sum(packet_header + data)
                fragmented_packets.append(packet_header + checksum + data)

        return fragmented_packets