from helpers import consts
import zlib

s = b'1110000001test.txt'
t = zlib.crc32(s)

# print(s[:2].decode())
# if s[:2] == b'11':
#     print('lol')
# print(str(t))
# print(b'11'+b'00')
# print('00001'.encode())
# print(len(b'2116'))
# target_host = "127.0.0.1" '583165432c'
# target_port = 2222 3297874395
#
# client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 328096778t
#
# client.sendto('1001000000013'.encode('utf-8'),(target_host,target_port))
#
# #msgFromServer = client.recvfrom(consts.PROTOCOL_SIZE)
# client.sendto("Hello from Client".encode('utf-8'),(target_host,target_port))
#
#
#
# msg = "Message from Server: {}".format(msgFromServer[0])
#
# print(msg)
#bytesObj = codecs.decode('48656c6c6f20576f726c64', 'hex_codec')
def create_frag_num(num):
    frag = num.to_bytes(6, 'big')
    # while len(frag) != 6:
    #     frag = "0" + frag
    return frag
print(create_frag_num(1))
if consts.NO_FRAGMENT == create_frag_num(0):
    print('lollol')