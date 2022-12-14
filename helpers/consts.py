"""
file that contains constants used in project
"""
# ------- Server consts -------
TARGET_HOST = "127.0.0.1"
TARGET_PORT = 2222
DOWNLOAD_PATH = './Downloads/'
FORMAT = 'utf-8'

# ------- Protocol consts -------
HEADER_SIZE = 14
PROTOCOL_SIZE = 1472
LOWEST_FRAGMENT_SIZE = 20

# ------- Packet Type -------
PACKET_TYPE_START = 0
PACKET_TYPE_END = 2
ACK = b'00'
FIN = b'01'
REQUEST = b'10'
DATA = b'11'

# ------- Msg type -------
MSG_TYPE_START = 2
MSG_TYPE_END = 4
NONE = b'00'
TXT = b'01'
FILE = b'10'
FAIL = b'11'

# ------ Frag num ------
FRAG_NUM_START = 4
FRAG_NUM_END = 10
NO_FRAGMENT = b'\x00\x00\x00\x00\x00\x00'
FIRST_FILE_PACKET = b'\x00\x00\x00\x00\x00\x01'
FRAG_NUM_LENGTH = 6

# ------ Check sum --------
CHECKSUM_START = 10
CHECKSUM_END = 14
CHECKSUM_LENGTH = 4
NO_CHECKSUM = b"0000"

# ------ Test consts --------
SIMULATION_TXT_NUM_OF_PACKETS = 8
SIMULATION_TXT_FRAGMENT_SIZE = 16
SIMULATION_FILE_FRAGMENT_SIZE = 50
SIMULATION_FILE_PATH = "./tests/simulation_file.txt"
