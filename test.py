import curses

stdscr = curses.initscr()
#curses.noecho()
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

con1.refresh()
con2.refresh()

try:
	while True:
		a = con2.getch()
		if a == 27: break
except:
	pass

curses.nocbreak()
stdscr.keypad(0)
curses.echo()
curses.endwin()


