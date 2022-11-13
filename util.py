import ipaddress
import os

from consts import PROTOCOL_SIZE, LOWEST_FRAGMENT_SIZE


def validate_ip_address(ip_string):
    try:
        ip_object = ipaddress.ip_address(ip_string)
        return True
    except ValueError:
        return False


def validate_port(port):
    try:
        port = int(port)
    except Exception:
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
    except Exception:
        return False
    if size < LOWEST_FRAGMENT_SIZE or size > PROTOCOL_SIZE:
        return False
    return True


def validate_file_path(path):
    check = os.path.exists(path)
    return check
