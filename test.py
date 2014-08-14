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
con2 = curses.newwin(3, size_x-2, size_y-4, 1)
con1.scrollok(True)
con2.scrollok(True)

con2.keypad(1)

con1.refresh()
con2.refresh()

messages = []

try:
	msg = ''
	while True:
		a = con2.getch()
		if a == 27: break
		elif a in (curses.KEY_BACKSPACE, 0x7f):
			y, x = con2.getyx()
			if len(msg) > 0: msg = msg[0:-1]
			if y > 0 and x == 0:
				con2.addstr(y-1, size_x-3, ' ')
				con2.move(y-1, size_x-3)
			elif x > 0:
				con2.addstr(y, x-1, ' ')
				con2.move(y, x-1)
		elif a in (ord('\n'), ord('\r'), curses.KEY_ENTER):
			messages += [msg]
			msg = ''
			con2.clear()
		elif a == curses.KEY_UP:
			#con2.scroll(-1)
			pass
		elif a == curses.KEY_DOWN:
			#con2.scroll(1)
			pass
		else:
			con2.addstr(chr(a))
			msg += chr(a)
except:
	pass

curses.nocbreak()
stdscr.keypad(0)
curses.echo()
curses.endwin()

print messages
