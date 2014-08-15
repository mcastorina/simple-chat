from socket import *

s = socket()
host = raw_input('Server: ')
port = int(raw_input('Port: '))
print 'Connecting to', host+':'+str(port)

s.connect((host, port))
print s.recv(1024)
s.send("Hello from client")

while True:
	s.send(raw_input('> '))

# Multi-threading
# One thread to listen for incoming messages
# One thread for sending messages

