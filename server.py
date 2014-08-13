from socket import *

s = socket()
host = ''
port = 1234
s.bind((host, port))

s.listen(5)
while True:
	c, addr = s.accept()
	print 'Connected from', addr
	c.send('Thank you for connecting')
	c.close()

# Multi-threading
# One thread to accept incoming connections
# One thread per client to listen for incoming messages

