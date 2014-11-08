import curses, sys, time, threading, Queue
from chat import SChat


# LAYOUT ------------------------------------- #

################################################
# win1---------------------------------------- #
# |                                          | #
# | con1                                     | #
# |                                          | #
# |                                          | #
# |                                          | #
# |                                          | #
# |                                          | #
# -------------------------------------------- #
# win2---------------------------------------- #
# |                                          | #
# | con2                                     | #
# |                                          | #
# -------------------------------------------- #
################################################

if len(sys.argv) != 3:
	print 'Usage: python chat-gui.py host port'
	print 'Example:\n\tpython chat-gui.py 192.168.254.1 1234'
	sys.exit()

# Initialize SChat
chat = SChat(sys.argv[1], int(sys.argv[2]))
chat.connect()

# Initialize GUI
stdscr = curses.initscr()
curses.noecho()
curses.nonl()
size_y, size_x = stdscr.getmaxyx()
if size_x < 4 or size_y < 9:
	print 'Please enlarge the terminal.'
	sys.exit(0)

# Initialize win1
win1 = curses.newwin(size_y*4/5, size_x, 0, 0)
win1.border()
win1.addstr(0, 1, 'Text')
win1.refresh()

# Initialize win2
win2 = curses.newwin(size_y/5+1, size_x, size_y*4/5, 0)
win2.border()
win2.addstr(0, 1, 'Input')
win2.refresh()

# Initialize con1
con1 = curses.newwin(size_y*4/5-2, size_x-2, 1, 1)
con1.scrollok(True)
con1.move(0,0)
con1.refresh()

# Initialize con2
con2 = curses.newpad(10, size_x-2)
con2_pos = 0
con2.keypad(1)
def c2refr(): con2.refresh(con2_pos, 0, size_y*4/5+1, 1, size_y-2, size_x-2)
c2refr()
con2.keypad(1)

# Create thread for incoming messages
messages = []
def wait_for_message(chat, messages):
	while True:
		try:
			info = chat.dlog.get(True, 5)
			con1.addstr(str(info)+'\n')
			con1.refresh()
			c2refr()
			messages += [info]
		except Queue.Empty: pass

thread = threading.Thread(target=wait_for_message, args=(chat,messages))
thread.daemon = True
thread.start()

msg = ''
while True:
	cmd = con2.getch()
	if cmd == 27: break # ESC
	elif cmd in (curses.KEY_BACKSPACE, 0x7f, 0x08):
		y,x = con2.getyx()
		if len(msg) > 0:
			msg = msg[0:-1]
			if x == 0 and y-con2_pos == 1 and con2_pos > 0:
				con2_pos -= 1
		if y > 0 and x == 0:
			con2.addstr(y-1, size_x-3, ' ')
			con2.move(y-1, size_x-3)
		elif x > 0:
			con2.addstr(y, x-1, ' ')
			con2.move(y, x-1)
		c2refr()
	elif cmd in (ord('\n'), ord('\r'), curses.KEY_ENTER):
		chat.send(msg)
		msg = ''
		con2.clear()
		c2refr()
	elif len(msg) < (size_x-2)*10 and cmd <= 255:
		y, x = con2.getyx()
		if y-con2_pos == 2 and x == size_x-3:
			con2_pos += 1
		con2.addstr(chr(cmd))
		msg += chr(cmd)
		c2refr()

curses.nocbreak()
stdscr.keypad(0)
curses.echo()
curses.endwin()
chat.close()

print messages
print chat.dlog.queue
