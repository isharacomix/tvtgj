# The SDL GFX module is a text-based curses-like library built on top of Pygame.
# This should be easier for windows users to utilize. We require both pygame and
# the optional Pygame font package.

import pygame
if pygame.font is None:
    raise Exception("Missing pygame.font module")

from core import log


# API:
#   start()
#   stop()
#   mode()
#   get_input()
#   clear()
#   draw(x,y,c,col)


# The "screen" used by Pygame. These private variables serve to do some of the
# optimization of Curses. The 'fakescreen' keeps track of cells that have not
# changed, and the dirty list shows all of the rectangles that should be
# updated on the screen.
_screen = None
_fakescreen = {}
_dirty = []


# The Start function creates a 24x80 tile surface attached to the window and
# programmatically generates a font tile for each color and boldness.
_tiles = None
_colors = { "x": (0,0,0),
            "r": (200,0,0),
            "g": (0,200,0),
            "y": (200,200,0),
            "b": (0,0,200),
            "m": (200,0,200),
            "c": (0,200,200),
            "w": (200,200,200),
    }
def start():
    global _screen, _tiles, _colors, _fakescreen, _dirty
    if not _screen:
        pygame.init()
        pygame.key.set_repeat(500,100)
        _screen = pygame.display.set_mode((800,720))
        _screen.fill((0,0,0))
        _fakescreen = {}
        _dirty = []
        
        if _tiles is None:
            f = pygame.font.Font(None,28)
            _tiles = {}
            for c in (" abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"+
                      "1234567890-=\\[];',./`~!@#$%^&*()_+|{}:\"<>?"):
             for fg in "xrgybmcw":
              for bg in "xrgybmcw":
               for bold in [False,True]:
                f.set_bold(bold)
                fg_col = _colors[fg]
                bg_col = _colors[bg]
                if bold:
                    fg_col = fg_col[0]+50,fg_col[1]+50,fg_col[2]+50
                
                # Here we render the character and align it to our grid.
                s1 = f.render(c,True,fg_col,bg_col).convert()
                w,h = s1.get_size()
                w = min(w,8)
                s1 = pygame.transform.smoothscale(s1.convert(),(w,28))
                s2 = pygame.Surface((10,30))
                s2.fill(bg_col)
                s2.blit(s1, (8-w,0) )
                
                # Store the surface in the tiles dictionary.
                _tiles[(c,fg,bg,bold)] = s2.convert()

# This turns off Pygame.
def stop():
    global _screen
    if _screen:
        pygame.quit()
        _screen = None

# Return the gfx mode. This mode is sdl, as opposed to curses.
def mode():
    return "sdl"

# Gets input from the user and translates it into python strings.
# Returns None if the user hasn't pressed anything. Ideally this would
# be intercepted by a keymapper object that doesn't rely on any literal
# key definitions. We only handle the first event in the events queue.
_keymap ={pygame.K_BACKSPACE: "backspace",
          pygame.K_UP:        "up",
          pygame.K_DOWN:      "down",
          pygame.K_LEFT:      "left",
          pygame.K_RIGHT:     "right",
          pygame.K_RETURN:    "enter",
          pygame.K_END:       "end",
          pygame.K_HOME:      "home",
          pygame.K_F1:        "f1",
          pygame.K_F2:        "f2",
          pygame.K_F3:        "f3",
          pygame.K_F4:        "f4",
          pygame.K_F5:        "f5",
          pygame.K_F6:        "f6",
          pygame.K_F7:        "f7",
          pygame.K_F8:        "f8",
          pygame.K_F9:        "f9",
          pygame.K_F10:       "f10",
          pygame.K_F11:       "f11",
          pygame.K_F12:       "f12",
          pygame.K_F13:       "f13",
          pygame.K_F14:       "f14",
          pygame.K_F15:       "f15",
          pygame.K_PAGEUP:    "page_up",
          pygame.K_PAGEDOWN:  "page_down",
          pygame.K_ESCAPE:    "escape",
          -1:                 None}
def get_input():
    global _screen, _keymap
    if _screen:
        events = pygame.event.get(pygame.KEYDOWN)
        quit = pygame.event.get(pygame.QUIT)
        others = pygame.event.get()
        
        if len(quit) > 0: return "escape"
        elif len(events) == 0: return None
        elif events[0].key in _keymap: return _keymap[events[0].key]
        else:
            try:
                return "%s"%events[0].unicode
            except:
                pass
    
    return None

# This redraws the screen and handles the framerate. Should be called once
# per game tick.
def refresh():
    global _screen, _dirty
    if _screen:
        pygame.time.wait(20)
        if len(_dirty) > 0:
            pygame.display.update(_dirty)
            _dirty = []

# Clear the screen.
def clear():
    global _screen, _dirty, _fakescreen
    if _screen:
        _screen.fill((0,0,0))
        _dirty.append(_screen.get_rect())
        _fakescreen = {}

# Draw a character at X,Y. Includes boundary checking. You can also
# include color codes. Lowercase letters are foreground, uppercase are
# background. Use an ! for bold and ? for reverse
def draw(x,y,c,col=""):
    global _screen, _tiles, _dirty, _fakescreen
    if _screen:
        if _fakescreen.get((x,y)) != (c,col):
            target = pygame.Rect(x*10,y*30,10,30)
            bold = "!" in col
            fg = "w"
            bg = "x"
            for q in "xrgybmcw":
                if q in col: fg = q
            for q in "XRGYBMCW":
                if q in col: bg = q
            if "?" in col:
                fg,bg=bg,fg
            _screen.blit(_tiles[(c,fg,bg,bold)],target)
            _dirty.append(target)
            _fakescreen[(x,y)] = (c,col)

