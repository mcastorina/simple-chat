import socket, select, sys, threading, time

class Chat(threading.Thread):
	def __init__(self, host, port):
		threading.Thread.__init__(self)
		self.daemon = True
		self._stop = False
		self._s = self._p = None
		self.host = host
		self.port = port
		self.server = False
		self._sockets = []
		self.sent = []
		self.received = []
		self.RECV_BUFFER = 4096
	def connect(self):
		if self._stop:
			print 'The thread has exited.'
			return
		self._s = socket.socket()
		try: self._s.connect((self.host, self.port))
		except:
			self.server = True
			print 'Running as server.'
		
		if self.server:
			self._s.bind(('', self.port))
			self._s.listen(10)
			print "Waiting for connection from %s" % (self.host)
		else: print "Connected to %s" % (self.host)
		self._sockets = [self._s]
	def run(self):
		while not self._stop:
			rs, ws, es = select.select(self._sockets, [], [], 5)
			for sock in rs:
				if self.server:
					if sock == self._p:
						# Data received
						try:
							data = sock.recv(self.RECV_BUFFER)
							if data: self.received += [data]
						except:
							print 'error'
							sock.close()
							break
					else:
						# New connection
						self._p, addr = self._s.accept()
						hostname = ''
						try: hostname = socket.gethostbyaddr(addr[0])[0]
						except: pass
						if addr[0] != self.host and hostname != self.host:
							print 'Refusing'
							self._p.close()
							self._p = None
						else:
							self._sockets += [self._p]
				else:
					if sock == self._s:
						# Data received
						data = sock.recv(self.RECV_BUFFER)
						if data: self.received += [data]
						else:
							print 'error3'
							return
	def send(self, data):
		self.sent += [data]
		if self.server:
			try: self._p.send(data)
			except: print 'error4'
		else: self._s.send(data)
	def close(self):
		try:
			self._stop = True
			self.join()
			self._s.close()
			self._p.close()
		except: pass

if __name__ == '__main__':
	chat = Chat('localhost', 1234)
	chat.connect()
	chat.start()
	while True: pass

