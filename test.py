import curses

stdscr = curses.initscr()
curses.noecho()
curses.nonl()
stdscr.keypad(1)

size_y, size_x = stdscr.getmaxyx()
#stdscr.border()

win1 = curses.newwin(size_y-5, size_x, 0, 0)
win2 = curses.newwin(5, size_x, size_y-5, 0)
win1.border()
win2.border()
win1.addstr(0, 1, 'Text')
win2.addstr(0, 1, 'Input')
win1.refresh()
win2.refresh()

con1 = curses.newwin(size_y-7, size_x-2, 1, 1)
con1.scrollok(True)
con1.refresh()

con2 = curses.newpad(10, size_x-2)
#con2.scrollok(True)
con2_pos = 0
def c2ref(): con2.refresh(con2_pos, 0, size_y-4, 1, size_y-2, size_x-2)
c2ref()
con2.keypad(1)

messages = []

try:
	msg = ''
	while True:
		a = con2.getch()
		if a == 27: break
		elif a in (curses.KEY_BACKSPACE, 0x7f, 0x08):
			y, x = con2.getyx()
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
			c2ref()
		elif a in (ord('\n'), ord('\r'), curses.KEY_ENTER):
			messages += [msg]
			msg = ''
			con2.clear()
			c2ref()
		elif a == curses.KEY_UP:
			pass
		elif a == curses.KEY_DOWN:
			pass
		elif a == curses.KEY_LEFT:
			pass
		elif a == curses.KEY_RIGHT:
			pass
		elif len(msg) < (size_x-2)*10:
			y, x = con2.getyx()
			if y-con2_pos == 2 and x == size_x-3:
				con2_pos += 1
			con2.addstr(chr(a))
			msg += chr(a)
			c2ref()
except:
	pass

curses.nocbreak()
stdscr.keypad(0)
curses.echo()
curses.endwin()

print messages
