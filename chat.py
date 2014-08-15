import socket, select, sys

RECV_BUFFER = 4096

if __name__ == "__main__":
	s = p = None
	if len(sys.argv) != 3:
		print "Usage: python chat.py hostname port"
		sys.exit()
	host = sys.argv[1]
	port = int(sys.argv[2])
	server_up = True
	
	s = socket.socket()
	p = None
	try:
		s.connect((host, port))
	except:
		server_up = False

	if server_up:
		print "Connected to server."
	else:
		s.bind(('', port))
		s.listen(10)
		print "Waiting for connection from %s" % (host)
	
	sockets = [s, sys.stdin]
	while True:
		read_sockets, write_sockets, error_sockets = select.select(sockets, [], [])
		for sock in read_sockets:
			if server_up:
				if sock == s:
					# Received message
					data = sock.recv(RECV_BUFFER)
					if not data:
						print 'Server closed.'
						sys.exit()
					else:
						sys.stdout.write(data)
				else:
					msg = sys.stdin.readline()
					s.send(msg)
			else:
				if sock == s:
					# New connection
					p, addr = s.accept()
					hostname = ''
					try: hostname = socket.gethostbyaddr(addr[0])[0]
					except: pass
					if addr[0] != host and hostname != host:
						print 'Received connection from %s, refusing.' % (addr[0])
						p.close()
					else:
						sockets += [p]
						print 'Connection established with %s' % (addr[0])
				elif sock == p:
					# Data received
					try:
						data = sock.recv(RECV_BUFFER)
						if data: sys.stdout.write(data)
					except:
						print 'Disconnected.'
						sock.close()
						break
				else:
					msg = sys.stdin.readline()
					try: p.send(msg)
					except:
						print 'Disconnected.'
						sys.exit()
	#if s: s.close()
	#if p: p.close()


# alice: AE
# bob:	 BE
# alice: cert
# bob:	 BS(hash(cert)), cert2
# alice: AS(hash(cert2))
# alice: BE(SK)

# Two threads: one handles sending messages, the other handles receiving messages (via select)

