import socket
import threading

class Server(threading.Thread):
    TARGET_HOST = "127.0.0.1"
    TARGET_PORT = 2222

    def __init__(self, *args, **kwargs):
        super(Server, self).__init__(*args, **kwargs)
        self._stop = threading.Event()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind((self.TARGET_HOST, self.TARGET_PORT))
        self.server.settimeout(1)
        print("Listening on {} : {} (default)".format(self.TARGET_HOST, self.TARGET_PORT))

    def revive(self):
        print("Listening on {} : {} (default)".format(self.TARGET_HOST, self.TARGET_PORT))
        self._stop.clear()

    def pause(self):
        print("Server has been stopped")
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        while True:
            try:
                if self.stopped():
                    continue

                message, address = self.server.recvfrom(1024)

                clientMsg = "Client Message: {}".format(message)
                clientIP = "Client IP Address: {]".format(address)

                print(clientMsg)
                print(clientIP)
                # self.server.sendto(bytes('lol'), address)
            except TimeoutError:
                continue
