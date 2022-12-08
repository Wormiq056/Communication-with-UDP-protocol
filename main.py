from sender.client import Client
from helpers import util
from helpers.consts import TARGET_HOST, TARGET_PORT

from reciever.server import Server


class ProgramInterface:
    """
    main program class that can change between a sender and a receiver
    """

    def __init__(self) -> None:
        self.target_host = TARGET_HOST
        self.target_port = TARGET_PORT
        self.server = None
        self.connected = False
        self.client = None
        self.running = True
        self.choose_target()
        self.start_server()

    def start_server(self) -> None:
        """
        method that creates a server that will listen on given IP and port
        if server cannot be created for some reason program stops
        """
        try:
            self.server = Server()
            self.server.bind(self.target_host, self.target_port, self)
            self.server.start()
        except Exception as e:
            print("[INFO] Server did not start correctly")
            print(f"[ERROR] {e}")
            return
        self.command_loop()

    def command_loop(self) -> None:
        """
        main command loop that is used to send txt/file, close connection and exit the program
        """
        while self.running:
            try:
                command = input("[COMMAND]: ")
            except KeyboardInterrupt:
                print("[INFO] Closing program")
                if self.connected:
                    self.client.close()
                self.server.close()
                break
            if command == 'send':
                self.server.pause()
                if not self.client:
                    self.connected = True
                    self.client = Client(self)
                    try:
                        self.client.initialize()
                    except KeyboardInterrupt:
                        print('[INFO] Connection is closed')
                        print('[INFO] Message sending interrupted')
                        self.client.close()
                        self.connection_error()
                    except ConnectionResetError:
                        print('[ERROR] Looks like server has been turned off')
                        self.client.close()
                        self.connection_error()
                else:
                    try:
                        self.client.initialize()
                    except KeyboardInterrupt:
                        print('[INFO] Message sending interrupted')
                    except ConnectionResetError:
                        print('[ERROR] Looks like server has been turned off')
                        self.client.close()
                        self.connection_error()
                    except TimeoutError:
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
            elif command == "dir":
                print("[INFO] Changing receiver download path")
                self.server.change_download_path()
            else:
                if self.connected:
                    print("[ERROR] Invalid argument (try: send, close, dir, exit)")
                else:
                    print("[ERROR] Invalid argument (try: send, dir, exit)")

    def server_error(self) -> None:
        """
        method that is used to when a server error occurs to end program
        """
        self.running = False

    def connection_error(self) -> None:
        """
        method that is called when sender could not connect to the receiver
        """
        self.connected = False
        self.client = None

    def choose_target(self) -> None:
        """
        method that is used to get input from terminal and validate it
        """
        while True:
            host = (input("[INPUT] Choose server host(default 127.0.0.1): "))
            if host == "":
                break
            else:
                if util.validate_ip_address(host):
                    self.target_host = host
                    break
                print("[ERROR] Choose a valid IP address")
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


def main() -> None:
    try:
        app = ProgramInterface()
    except KeyboardInterrupt:
        # if app.connected:
        #     app.client.close()
        #     app.server.close()
        exit()

if __name__ == '__main__':
    main()
