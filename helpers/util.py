import ipaddress
import os
import zlib
import random

from helpers.consts import PROTOCOL_SIZE, LOWEST_FRAGMENT_SIZE, FRAG_NUM_LENGTH, CHECKSUM_END, CHECKSUM_START


def validate_ip_address(ip_string):
    try:
        ipaddress.ip_address(ip_string)
        return True
    except ValueError:
        return False


def validate_port(port):
    try:
        port = int(port)
    except ValueError:
        return False
    if port < 0 or port > 65535:
        return False
    return True


def validate_msg_type(msg_type):
    if msg_type == 'f' or msg_type == 't':
        return True
    return False


def validate_fragment_size(size):
    try:
        size = int(size)
    except ValueError:
        return False
    if size < LOWEST_FRAGMENT_SIZE or size > PROTOCOL_SIZE:
        return False
    return True


def validate_file_path(path):
    if path == "":
        return True
    check = os.path.exists(path)
    return check


def create_frag_from_num(num):
    return num.to_bytes(FRAG_NUM_LENGTH, 'big')


def create_check_sum(msg):
    checksum = zlib.crc32(msg).to_bytes(4, 'big')
    return checksum


def compare_checksum(msg):
    sent_checksum = msg[CHECKSUM_START:CHECKSUM_END]
    server_checksum = msg[:CHECKSUM_START] + msg[CHECKSUM_END:]
    if zlib.crc32(server_checksum).to_bytes(4, 'big') != sent_checksum:
        return False
    return True


