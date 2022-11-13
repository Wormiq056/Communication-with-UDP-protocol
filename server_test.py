import socket
import consts
import zlib

import consts

s = b'1110000001test.txt'
t = zlib.crc32(s)

print(str(t))

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