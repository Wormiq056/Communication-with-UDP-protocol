HEADER_SIZE = 20
PROTOCOL_SIZE = 1400
FORMAT = 'utf-8'
DOWNLOAD_PATH = "./Downloads/"

# ------- Packet Type -------
PACKET_TYPE_START = 0
PACKET_TYPE_END = 2
ACK = "00"
FIN = "01"
REQUEST = "10"
DATA = "11"

# ------- Msg type -------
MSG_TYPE_START = 2
MSG_TYPE_END = 4
NONE = "00"
TXT = "01"
FILE = "10"
FAIL = "11"

# ------ Frag num ------
FRAG_NUM_START = 4
FRAG_NUM_END = 10
NO_FRAGMENT = "000000"
FIRST_FILE_PACKET = "000001"

# ------ Check sum --------
CHECKSUM_START = 10
CHECKSUM_END = 20

