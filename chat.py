import socket, select, sys, threading, time, M2Crypto, os.path, hashlib, json, Queue

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
		self._received = Queue.Queue()
		self.log = Queue.Queue()
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
			while self._p == None:
				rs, ws, es = select.select([self._s], [], [], 5)
				for sock in rs:
					if sock == self._s:
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
							self._sockets = [self._s, self._p]
						
		else:
			print "Connected to %s" % (self.host)
			self._sockets = [self._s]
		self.start()
	def run(self):
		while not self._stop:
			rs, ws, es = select.select(self._sockets, [], [], 5)
			for sock in rs:
				if self.server and sock == self._p:
					# Server - Data _received
					try:
						data = sock.recv(self.RECV_BUFFER)
						if data:
							self._received.put(data)
							self.log.put(('Received - '+time.ctime(), data))
					except:
						print 'error'
						sock.close()
						break
				elif not self.server and sock == self._s:
					# Client - Data _received
					data = sock.recv(self.RECV_BUFFER)
					if data:
						self._received.put(data)
						self.log.put(('Received - '+time.ctime(), data))
					else:
						print 'error3'
						return
	def send(self, data):
		self.log.put(('Sent - '+time.ctime(), data))
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
		self._sk = self._ek = None
		self.dlog = Queue.Queue()
		if not os.path.isfile('id-rsa') or not os.path.isfile('id-rsa.pub'):
			self._generate_rsa_keypair()
		self._sk = M2Crypto.RSA.load_key('id-rsa')
	def _generate_rsa_keypair(self, bits=2048):
		new_key = M2Crypto.RSA.gen_key(bits, 3)
		new_key.save_key('id-rsa', cipher=None)
		new_key.save_pub_key('id-rsa.pub')
	def _rsa_encrypt(self, data):
		return self._ek.public_encrypt(data, M2Crypto.RSA.pkcs1_oaep_padding)
	def _rsa_decrypt(self, v):
		return self._sk.private_decrypt(v, M2Crypto.RSA.pkcs1_oaep_padding)
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
		data = data + cipher.final()
		del(cipher)
		return data
	def _handhsake(self, peer):
		pass
	def connect(self):
		Chat.connect(self)
		# ---------------------------Handhsake------------------------- #
		pub_key = M2Crypto.RSA.load_pub_key('id-rsa.pub')
		memory = M2Crypto.BIO.MemoryBuffer()
		pub_key.save_pub_key_bio(memory)
		pub_key_bio = memory.getvalue()
		pub_key_fp = hashlib.sha1(bytes(pub_key_bio)).hexdigest()
		cert = time.ctime() + M2Crypto.Rand.rand_bytes(128)
		# Send fingerprint
		self.send_raw(pub_key_fp)
		# Check known-hosts for fingerprint
		while self._received.qsize() == 0: pass
		pub_key_fp = self._received.get()
		unknown = True
		known_hosts = {}
		try:
			fp = open('known-hosts', 'r')
			known_hosts = json.loads(fp.read())
			fp.close()
			for k, v in known_hosts.iteritems():
				if pub_key_fp in v.values():
					memory.write(str(k))
					self._ek = M2Crypto.RSA.load_pub_key_bio(memory)
					unknown = False
					break
		except: print 'file error'
			
		# If found, request certificate
		# Else, request public key
		if unknown:
			self.send_raw('public key')
		else:
			self.send_raw('certificate')
		
		# Send public key and certificate
		while self._received.qsize() == 0: pass
		task = self._received.get()
		if task == 'public key':
			self.send_raw(pub_key_bio)
		self.send_raw(cert)
		# Save peer's public key
		if unknown:
			while self._received.qsize() == 0: pass
			pk = self._received.get()
			if raw_input('Add %s to known-hosts? (y/n): ' % self.host) == 'y':
				known_hosts[pk] = {"SHA-1": hashlib.sha1(bytes(pk)).hexdigest()}
				fp = open('known-hosts', 'w')
				fp.write(json.dumps(known_hosts, sort_keys=True, indent=4, separators=(',', ': ')))
				fp.close()
			memory.write(pk)
			self._ek = M2Crypto.RSA.load_pub_key_bio(memory)
		# Sign certificate
		while self._received == 0: pass
		pcert = self._received.get()
		signature = self._sk.sign_rsassa_pss(pcert)
		self.send_raw(signature)
		# Verify peer's signature
		while self._received.qsize() == 0: pass
		psign = self._received.get()
		try:
			if self._ek.verify_rsassa_pss(cert, psign):
				print "Verified"
			else:
				print "Not verified"
				self.close()
				return
		except:
			self.close()
			return
		# Agree on a symmetric key
		if self.server:
			self._generate_sym_key()
			self.send_raw(self._rsa_encrypt(self.key))
			self.send_raw(self._rsa_encrypt(self.iv))
		else:
			while self._received.qsize() < 2: pass
			self.key = self._rsa_decrypt(self._received.get())
			self.iv = self._rsa_decrypt(self._received.get())
		self._dthread = threading.Thread(target=self._decrypt_pending_data)
		self._dthread.daemon = True
		self._dthread.start()

	def send(self, data):
		self.dlog.put(('Sent - '+time.ctime(), data))
		Chat.send(self, self._aes_encrypt(data))
	def send_raw(self, data):
		Chat.send(self, data)
		time.sleep(0.25)
	def _decrypt_pending_data(self):
		while not self._stop:
			# Queue.Queue.get by default blocks until getting an item
			try:
				data = self._aes_decrypt(self._received.get(True, 5))
				self.dlog.put(('Decrypted - '+time.ctime(), data))
			except: pass
	def close(self):
		Chat.close(self)
		try: self._dthread.join()
		except: pass
