import signal
import time
from server import Server
import os


def main():
    server = Server()
    server.start()

    while True:
        command = input("")
        if command == 'send':
            server.pause()
            time.sleep(3)
            server.revive()
        elif command == 'exit':
            print("Closing program")
            os.kill(os.getpid(), signal.SIGINT)
        elif command == "pause":
            server.pause()
        elif command == "revive":
            server.revive()
        else:
            print("Invalid argument (try: send, pause, revive, exit)")


if __name__ == '__main__':
    main()
