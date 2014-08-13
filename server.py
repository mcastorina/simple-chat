from socket import *

s = socket()
#host = gethostname()
host = '192.168.254.2'
port = 1234
s.bind((host, port))

s.listen(5)
while True:
	c, addr = s.accept()
	print 'Connected from', addr
	c.send('Thank you for connecting')
	c.close()


