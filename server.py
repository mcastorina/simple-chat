import socket, threading, Queue

def wait_for_connections(q, s):
	while True:
		c, addr = s.accept()
		print 'Connected from', addr
		c.send('Thank you for connecting')
		q.put((c, addr))

def wait_for_input(client):
	while True:
		c, addr = client
		message = c.recv(1024)
		if len(message) == 0: continue
		print addr, message

def create_client(q):
	while True:
		t = threading.Thread(target=wait_for_input, args=(q.get(),))
		t.daemon = True
		t.start()

s = socket.socket()
host = ''
port = 1234
s.bind((host, port))
s.listen(5)

q1 = Queue.Queue()

thread1 = threading.Thread(target=wait_for_connections, args=(q1, s))
thread1.daemon = True
thread1.start()

thread2 = threading.Thread(target=create_client, args=(q1,))
thread2.daemon = True
thread2.start()

while True:
	pass

# Multi-threading
# One thread to accept incoming connections
# One thread per client to listen for incoming messages

