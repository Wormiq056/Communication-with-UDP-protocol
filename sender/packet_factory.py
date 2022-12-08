import os
import random
import string

from typing import List
from helpers import util
from helpers.consts import HEADER_SIZE, TXT, FILE, DATA, NO_FRAGMENT, FORMAT, SIMULATION_TXT_NUM_OF_PACKETS, \
    SIMULATION_TXT_FRAGMENT_SIZE


class PacketFactory:
    """
    class that creates packets for message we want to transfer
    """

    @staticmethod
    def create_txt_packets(fragment_size: int, msg: str) -> List[bytes]:
        """
        method that creates txt packet or packets if message needs to be fragmented
        :param fragment_size: what will be the fragment size
        :param msg: message we want to send
        :return: packets created from message
        """
        #shifted_msg = PacketFactory.shift(msg, 3)
        fragmented_packets = []
        #msg = "_BEGIN_" + shifted_msg + "_END_"
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
    def shift(text, s):
        result = ""
        for i in range(len(text)):
            char = text[i]
            if (char.isupper()):
                result += chr((ord(char) + s) % 128)
            else:
                result += chr((ord(char) + s) % 128)
        return result

    @staticmethod
    def create_file_packets(file_path: str, fragment_size: int) -> List[bytes]:
        """
        method that creates packets from file we want to send
        :param file_path: path to file
        :param fragment_size: what will be the fragment size
        :return: list of created file packets
        """
        packet_msg = os.path.basename(file_path).encode(FORMAT)
        first_header = DATA + FILE + util.create_frag_from_num(1)
        buffer = (fragment_size - HEADER_SIZE)
        checksum = util.create_check_sum(first_header + packet_msg)
        fragmented_packets = [first_header + checksum + packet_msg]
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
    def create_simulation_txt_packets() -> str and List[bytes]:
        """
        method that creates random message for error simulation
        :return: list of txt packets
        """
        simulation_packets = []
        generated_msg = ""
        for i in range(SIMULATION_TXT_NUM_OF_PACKETS):
            msg = ''.join(
                random.choices(string.ascii_uppercase + string.digits,
                               k=SIMULATION_TXT_FRAGMENT_SIZE - HEADER_SIZE)).encode(
                FORMAT)
            generated_msg = generated_msg + msg.decode(FORMAT)
            packet_header = DATA + TXT + util.create_frag_from_num(i + 1)
            checksum = util.create_check_sum(packet_header + msg)
            simulation_packets.append(packet_header + checksum + msg)

        return generated_msg, simulation_packets
