import socket, select, sys, threading, time, M2Crypto, os.path

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
			self._s = socket.socket()
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

class SChat(Chat):
	def __init__(self, host, port):
		Chat.__init__(self, host, port)
		self.ENC = 1
		self.DEC = 0
		self.key = None
		self.iv = None
		self._sk = 'id-rsa'
		self._ek = 'id-rsa.pub'
		if not os.path.isfile(self._sk) or not os.path.isfile(self._ek):
			self._generate_rsa_keypair()
	def _generate_rsa_keypair(self, bits=2048):
		new_key = M2Crypto.RSA.gen_key(bits, 65537)
		new_key.save_key('id-rsa', cipher=None)
		new_key.save_pub_key('id-rsa.pub')
	def _rsa_encrypt(self, data):
		return M2Crypto.RSA.load_pub_key(self._ek).public_encrypt(data, M2Crypto.RSA.pkcs1_oaep_padding)
	def _rsa_decrypt(self, v):
		return M2Crypto.RSA.load_key(self._sk).private_decrypt(v, M2Crypto.RSA.pkcs1_oaep_padding)
	def _generate_sym_key(self):
		self.key = M2Crypto.Rand.rand_bytes(32)
		self.iv = M2Crypto.Rand.rand_bytes(16)
	def _generate_cipher(self, op):
		return M2Crypto.EVP.Cipher(alg='aes_256_cbc', key=self.key, iv=self.iv, op=op)
	def _aes_encrypt(self, data):
		cipher = self._generate_cipher(self.ENC)
		v = cipher.update(data)
		v = v + cipher.final()
		del(cipher)
		return v
	def _aes_decrypt(self, v):
		cipher = self._generate_cipher(self.DEC)
		data = cipher.update(v)
		data = msg + cipher.final()
		del(cipher)
		return data
	def _handhsake(self, peer):
		pass
	def connect(self):
		Chat.connect(self)
