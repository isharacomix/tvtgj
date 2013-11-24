
import curses

screen = None

# This starts up curses.
def start():
    global screen
    screen = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    screen.keypad(1)
    screen.timeout(0)


def stop():
    global screen
    curses.nocbreak()
    screen.timeout(-1)
    screen.keypad(0)
    curses.curs_set(1)
    curses.echo()
    curses.endwin()
    screen = None


def scr():
    global screen
    return screen

