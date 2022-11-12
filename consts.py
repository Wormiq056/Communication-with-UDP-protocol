HEADER_SIZE = 19
PROTOCOL_SIZE = 1400
FORMAT = 'utf-8'


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
FRAG_NUM_END = 9
NO_FRAGMENT = "00000"

# ------ Check sum --------
CHECKSUM_START = 9
CHECKSUM_END = 19

