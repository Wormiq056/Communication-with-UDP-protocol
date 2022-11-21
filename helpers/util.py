import ipaddress
import os
import zlib

from helpers import consts


def validate_ip_address(ip_string: str) -> bool:
    """
    helper function that validates given IP address format
    :param ip_string: IP address you want to validate
    :return: boolean result
    """
    try:
        ipaddress.ip_address(ip_string)
        return True
    except ValueError:
        return False


def validate_port(port: str) -> bool:
    """
    helper function that checks if inputted port is valid
    :param port: port you want to validate
    :return: bool result
    """
    try:
        port = int(port)
    except ValueError:
        return False
    if port < 0 or port > 65535:
        return False
    return True


def validate_msg_type(msg_type: str) -> bool:
    """
    helper function that validates if msg type is correct
    :param msg_type: validation
    :return: bool result
    """
    if msg_type == 'f' or msg_type == 't':
        return True
    return False


def validate_fragment_size(size: str) -> bool:
    """
    function that validates given fragment size
    :param size: fragment size you want to validate
    :return: bool result
    """
    try:
        size = int(size)
    except ValueError:
        return False
    if size < consts.LOWEST_FRAGMENT_SIZE or size > consts.PROTOCOL_SIZE:
        return False
    return True


def validate_file_path(path: str) -> bool:
    """
    function that checks if given path to file exists or if you want to run simulation
    :param path: path to check
    :return: bool result
    """
    if path == "":
        return True
    check = os.path.exists(path)
    if os.path.isdir(path):
        return False
    return check


def create_frag_from_num(num: int) -> bytes:
    """
    helper function that returns bytes from given int
    """
    return num.to_bytes(consts.FRAG_NUM_LENGTH, 'big')


def create_check_sum(msg: bytes) -> bytes:
    """
    helper function that returns given str in bytes
    """
    checksum = zlib.crc32(msg).to_bytes(4, 'big')
    return checksum


def compare_checksum(msg: bytes) -> bool:
    """
    helper function that compares checksum of sent packet with checksum of received packet
    :param msg: received packet
    :return: check result
    """
    sent_checksum = msg[consts.CHECKSUM_START:consts.CHECKSUM_END]
    server_checksum = msg[:consts.CHECKSUM_START] + msg[consts.CHECKSUM_END:]
    if zlib.crc32(server_checksum).to_bytes(4, 'big') != sent_checksum:
        return False
    return True


def change_download_path() -> None:
    """
    function that validates download path and calls another function to change it
    """
    while True:
        download_path = input('[INPUT] New download path: ')
        if download_path == "":
            break
        check = os.path.exists(download_path)
        if not os.path.isdir(download_path):
            print('[INFO] Path is not a dir')
            continue
        if not check:
            print('[INFO] Path does not exists')
            continue
        if download_path[-1] != "/":
            download_path += "/"
        consts.change_download_path(download_path)
        break

