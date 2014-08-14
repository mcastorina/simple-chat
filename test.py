import curses


stdscr = curses.initscr()
curses.noecho()
curses.nonl()
stdscr.keypad(1)

size_y, size_x = stdscr.getmaxyx()
#stdscr.border()
stdscr.move(size_y-1, 0)
stdscr.addstr('> ')
messages = []
try:
	msg = ''
	while True:
		a = stdscr.getch()
		if a == 27: break
		elif a in (curses.KEY_BACKSPACE, 0x7f):
			y, x = stdscr.getyx()
			if x > 2:
				stdscr.addstr(y, x-1, ' ')
				stdscr.move(y, x-1)
				msg = msg[0:-1]
		elif a == ord('\n') or a == ord('\r'):
			if len(msg) != 0:
				stdscr.addstr(size_y-1, 2, ' '*len(msg))
				stdscr.addstr(len(messages), 0, '| '+msg)
				messages += [msg]
				msg = ''
			stdscr.move(size_y-1, 2)
		else:
			stdscr.addstr(chr(a))
			msg += chr(a)
except:
	pass

curses.nocbreak()
stdscr.keypad(0)
curses.echo()
curses.endwin()

print messages

