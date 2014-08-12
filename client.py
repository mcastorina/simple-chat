# import socket
# import sys

# HOST = '192.168.254.6'
# PORT = 50007
# s = None
# for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
	# af, socktype, proto, canonname, sa = res
	# try:
		# s = socket.socket(af, socktype, proto)
	# except socket.error, msg:
		# s = None
		# continue
	# try:
		# s.bind(sa)
	# except socket.error, msg:
		# s.close()
		# s = None
		# continue
	# break
# if s is None:
	# print 'could not open socket'
	# sys.exit(1)
# s.send('Hello world')
# data = s.recv(1024)
# s.close()
# print 'Received', repr(data)

import socket

HOST = 'localhost'
PORT = 50007

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
inp = ''

usr = raw_input('Username: ')
psw = raw_input('Password: ')

s.send(usr)
s.send(psw)

alw = s.recv(1024)
print(alw)

while inp != 'exit' and alw == 'Accepted':
	inp = raw_input('> ')
	s.send(inp)
s.close()