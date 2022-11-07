import signal
import time
from server import Server
import os


def main():
    server = Server()
    server.start()

    while True:
        command = input("command:")
        if command == 'send':
            server.pause()
            time.sleep(3)
            server.revive()
        elif command == 'exit':
            print("Closing program")
            os.kill(os.getpid(), signal.SIGINT)



if __name__ == '__main__':
    main()
