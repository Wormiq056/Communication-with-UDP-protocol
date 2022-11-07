import socket
target_host = "127.0.0.1"
target_port = 2222

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client.sendto("Hello from Client".encode('utf-8'), (target_host,target_port))

msgFromServer = client.recvfrom(1024)

msg = "Message from Server: {}".format(msgFromServer[0])

print(msg)