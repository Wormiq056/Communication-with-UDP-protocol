In this project I created my own protocol based un UDP protocol. Program can work like a server and client and transfer text messages or files between. 


This is an explanation of my protocol. It enables you to transfer text messages and files which are under 1 TB size(
this will not work however because you will most likely run out of RAM at that point). It works on a simple principle
which is that it contains packet type, message type, fragment number, checksum and data.

Packet type is used to determine packet's main functionality. ACK packets are used to acknowledge correct transfer of
sent packets as well as to keep connection between client and the server. Client sends an ACK packet every 5 seconds
to signal the server that it still potentially wants to send messages. FIN packets are used to tell server that one
message or file transfer was finished and is ready to be processed. REQUEST packets are used to request for a connection
or when a packet is lost or corrupted they are used to inform the client to resend packets again. DATA packets as the
name suggest are used to transfer raw bytes to the server.

Message type is used to categorize what type of message was sent. FILE means we are transferring file data. TXT means
we are transferring text data. NONE means no data is transferred - these packets are meant to keep connection or request
a connection. FAIL message type is used to tell is some type of error occurred during transfer .

Fragment number is used to determine if message will be transferred or not and what is its fragment number. If fragment
number is 0 the server will know that that is the only packet it will receive for that message transfer. This can only
happen however if we are sending a small text message. Fragment number can go up to 2**48.

Checksum represents a 32-bit long integer that is returned from zlib.crc32() function. It is compared whenever a packet
is received (on both sides). If for some reason the compared number do not match program asks for a resend of packets


Packet visualization:
-----------------------------------------------
|packet type|msg type|frag num|checksum|data|
-----------------------------------------------
HEADER-SIZE = 14 B
packet type (2 bytes) = ACK, FIN, REQUEST, DATA
msg type (2 bytes) = FILE, TEXT, NONE, FAIL
frag num (6 bytes) = num of current fragment
checksum (4 bytes) = checksum of packet
data (0-1458 bytes) = message data we want to sent

----packet type----
ACK = 00
FIN = 01
REQUEST = 10
DATA = 11

----msg type----
NONE = 00
TXT = 01
FILE = 10
FAIL = 11

---frag num----
number x  (0 <x> 2**48)

---checksum---
checksum of packet data

---data---
data sent




More information in documentation
