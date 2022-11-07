import time
from server import Server


def main():
    server = Server()
    server.start()



    while True:

        command = input("command:")
        if command == 'send':
            server.pause()
            time.sleep(3)

        server.revive()

if __name__ == '__main__':
    main()