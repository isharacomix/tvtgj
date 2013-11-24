
from core import gfx

import sys
import traceback
import curses

# A Game represents a single instance of a game, including its maps,
# data, and everything else.
class Game(object):
    def __init__(self):
        pass
    
    def step(self):
        running = True
        x,y = 0,0
        while running:
            c = gfx.scr().getch()
            if c == curses.KEY_UP:      y -= 1
            elif c == curses.KEY_DOWN:  y += 1
            elif c == curses.KEY_LEFT:  x -= 1
            elif c == curses.KEY_RIGHT: x += 1
            elif c == ord('q'): running  = False
            
            if c != -1:
                gfx.scr().clear()
                gfx.scr().addch(y,x,"@")

    
    
    # Runs an interactive session of our game with the player.
    def play(self):
        gfx.start()
        
        try: 
            self.step()
        except:
            gfx.stop()  
            print(traceback.format_exc())
            sys.exit(-1)
        
        gfx.stop()


