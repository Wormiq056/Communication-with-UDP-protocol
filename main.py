import signal
import time
from server import Server
import os
from client import Client

def main():
    try:
        server = Server()
        server.start()
    except Exception:
        pass
    client = None
    connected = False

    while True:
        command = input("")
        if command == 'send':
            try:
                server.pause()
            except Exception:
                pass
            if not client:
                connected = True
                client = Client()
                client.initialize()
            else:
                client.create_msg()
            time.sleep(3)
            try:
                server.revive()
            except:
                pass
        elif command == 'exit':
            print("Closing program")
            os.kill(os.getpid(), signal.SIGINT)
        elif command == "pause" and not connected:
            server.pause()
        elif command == "revive" and not connected:
            server.revive()
        elif command == "close" and connected:
            connected = False
            client.close()
            client = None

        else:
            if connected:
                print("Invalid argument (try: send, close, exit)")
            else:
                print("Invalid argument (try: send, pause, revive, exit)")


if __name__ == '__main__':
    main()
