from socket import *

s = socket()
host = raw_input('Server: ')
port = 1234
print 'Connecting to', host

s.connect((host, port))
print s.recv(1024)
s.close()

