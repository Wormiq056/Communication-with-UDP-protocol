import signal
import time
from server import Server
import os
from client import Client

def main():
    server = Server()
    server.start()
    client = None
    connected = False

    while True:
        command = input("")
        if command == 'send':
            server.pause()
            if not client:
                client = Client()
                client.initialize()
            else:
                client.create_msg()
            time.sleep(3)
            server.revive()
        elif command == 'exit':
            print("Closing program")
            os.kill(os.getpid(), signal.SIGINT)
        elif command == "pause" and not connected:
            server.pause()
        elif command == "revive" and not connected:
            server.revive()
        elif command == "close" and connected:
            client.close()
            client = None

        else:
            if connected:
                print("Invalid argument (try: send, close, exit)")
            else:
                print("Invalid argument (try: send, pause, revive, exit)")


if __name__ == '__main__':
    main()
