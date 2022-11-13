from reciever.server import Server
from sender.client import Client
from helpers import util
from helpers.consts import TARGET_HOST, TARGET_PORT


class ProgramInterface:
    target_host = TARGET_HOST
    target_port = TARGET_PORT
    server = None

    def __init__(self):
        self.connected = False
        self.client = None
        self.choose_target()
        self.start_server()

    def start_server(self):
        try:
            self.server = Server()
            self.server.bind(self.target_host, self.target_port)
            self.server.start()
        except Exception as e:
            print("[INFO] Server did not start correctly")
            print(f"[ERROR] {e}")
            return
        self.command_loop()

    def command_loop(self):
        while True:
            command = input("[COMMAND]:")
            if command == 'send':
                self.server.pause()
                if not self.client:
                    self.connected = True
                    self.client = Client(self)
                    self.client.initialize()
                else:
                    try:
                        self.client.create_msg()
                    except Exception:
                        print('[ERROR] Looks like server has been turned off')
                        self.client.close()
                        self.connection_error()
                self.server.revive()
            elif command == 'exit':
                print("[INFO] Closing program")
                if self.connected:
                    self.client.close()
                self.server.close()
                break
            elif command == "close" and self.connected:
                self.connected = False
                self.client.close()
                self.client = None
            else:
                if self.connected:
                    print("[ERROR] Invalid argument (try: send, close, exit)")
                else:
                    print("[ERROR] Invalid argument (try: send, exit)")

    def connection_error(self):
        self.connected = False
        self.client = None

    def choose_target(self):
        while True:
            host = (input("[INPUT] Choose server host(default 127.0.0.1): "))
            if host == "":
                break
            else:
                if util.validate_ip_address(host):
                    self.target_host = host
                    break
                print("[ERROR] Choose a valid IP adress")
        while True:
            port = (input("[INPUT] Choose server port(default 2222): "))
            if port == "":
                break
            else:
                if util.validate_port(port):
                    self.target_port = int(port)
                    break
                else:
                    print("[ERROR] Choose a valid port")


def main():
    app = ProgramInterface()


if __name__ == '__main__':
    main()
