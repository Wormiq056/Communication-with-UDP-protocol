import socket
#import consts
target_host = "127.0.0.1"
target_port = 2222

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((target_host,target_port))

client.send('1001000000013'.encode('utf-8'))
msgFromServer = client.recv(13)
client.send("Hello from Client".encode('utf-8'))



msg = "Message from Server: {}".format(msgFromServer[0])

print(msg)