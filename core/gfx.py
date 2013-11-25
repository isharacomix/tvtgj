# The ASCII GFX module handles curses for us so that we don't have to do it
# ourselves. It's not object-oriented, so we should only ever have one game
# object trying to use it at a time. It uses a singleton screen object that
# represents the terminal window.

import curses

# TODO: The 'draw' method is too dependent on the fact that there are tiles.
# We may have to include differences between world rendering and the GUI in 
# order to support tiles.


# The "screen" used by Curses. When "None", curses is off, and all curses
# commands silently (safely) fail. This way, we can run games in non-interactive
# mode.
screen = None


# This starts up curses and sets the terminal to stop doing things like
# echoing output. You can call start more than once safely.
def start():
    global screen
    if not screen:
        screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        curses.nonl()
        screen.keypad(1)
        screen.timeout(0)
        screen.scrollok(False)

# This turns off curses and makes it safe to kill the program. You can call
# stop more than once safely.
def stop():
    global screen
    if screen:
        screen.timeout(-1)
        screen.keypad(0)
        screen.scrollok(True)
        curses.nocbreak()
        curses.curs_set(1)
        curses.nl()
        curses.echo()
        curses.endwin()
        screen = None

# Get the screen object. This function probably shouldn't be used.
def scr():
    global screen
    return screen

# Return the gfx mode. This mode is curses.
def mode():
    global screen
    return "curses"

# Gets input from the user and translates it into python strings.
# Returns None if the user hasn't pressed anything. Ideally this would
# be intercepted by a keymapper object that doesn't rely on any literal
# key definitions.
keymap = {curses.KEY_BACKSPACE: "backspace",
          curses.KEY_UP:        "up",
          curses.KEY_DOWN:      "down",
          curses.KEY_LEFT:      "left",
          curses.KEY_RIGHT:     "right",
          curses.KEY_ENTER:     "\n",
          curses.KEY_END:       "end",
          curses.KEY_HOME:      "home",
          curses.KEY_F0:        "f0",
          curses.KEY_F1:        "f1",
          curses.KEY_F2:        "f2",
          curses.KEY_F3:        "f3",
          curses.KEY_F4:        "f4",
          curses.KEY_F5:        "f5",
          curses.KEY_F6:        "f6",
          curses.KEY_F7:        "f7",
          curses.KEY_F8:        "f8",
          curses.KEY_F9:        "f9",
          curses.KEY_F10:       "f10",
          curses.KEY_F11:       "f11",
          curses.KEY_F12:       "f12",
          curses.KEY_F13:       "f13",
          curses.KEY_F14:       "f14",
          curses.KEY_F15:       "f15",
          curses.KEY_RESIZE:    "resize",
          curses.KEY_PPAGE:     "page_up",
          curses.KEY_NPAGE:     "page_down",
          -1:                   None}
def get_input():
    global screen, keymap
    if screen:
        c = screen.getch()
        #curses.flushinp()
        if c > 0 and c < 256: return "%c"%c
        elif c in keymap: return keymap[c]
    return None

# Clear the screen. This uses Curses' optimized clear routine, so it's not
# necessarily inefficient.
def clear():
    global screen
    if screen:
        screen.erase()

# Draw a character at X,Y. Includes boundary checking.
def draw(x,y,c):
    global screen
    if screen:
        h,w = screen.getmaxyx()
        if x >= 0 and x < w and y >= 0 and y < h and (x,y)!=(w-1,h-1):
            screen.addch(y,x,c[0])



