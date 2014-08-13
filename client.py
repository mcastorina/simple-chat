from socket import *

s = socket()
host = raw_input('Server: ')
port = int(raw_input('Port: '))
print 'Connecting to', host+':'+str(port)

s.connect((host, port))
print s.recv(1024)
s.close()

# Multi-threading
# One thread to listen for incoming messages
# One thread for sending messages

