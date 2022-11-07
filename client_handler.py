import socket
import consts

class ClientHandler:
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        header_msg = conn.recv(consts.HEADER).decode(consts.FORMAT)
        if header_msg[:2] == '10':
            if header_msg[2:4] == '01':
                self.handle_text_transfer(header_msg)

    def handle_text_transfer(self, first_header):
        current_header = first_header
        print(current_header)
        communication = True
        respone = consts.ACK_MSQ.encode(consts.FORMAT)
        self.conn.send(respone)
        print(int(current_header[9:13]))
        # while communication:
        packet = self.conn.recv(consts.HEADER+int(current_header[9:13])).decode(consts.FORMAT)
        print(packet)