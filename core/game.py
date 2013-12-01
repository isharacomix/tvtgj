# The Game is where it all starts. A Game is an abstract and thin package in
# which all of the elements of the game are stored. It is responsible for
# creating the world, parsing and writing to save files, and turning on/off
# graphics.

from core import gfx
from core import world

import sys
import traceback


# A Game represents a single instance of a game, including its maps,
# data, and everything else.
class Game(object):
    def __init__(self):
        self.world = world.World()
    
    
    def display_title(self):
        title = [(1,"It'll never catch on!"),
                 (2,"A robot-battle roguelike (VERY) loosely based on TVTROPES"),
                 
                 (4,"    e r               y u     "),
                 (5,"   s   f             h   k    "),
                 (6,"    x c               b n     "),
                 (7,"'Left stick'     'Right stick'"),
                 (8," Aim Target        Move Robot "),

                (10,"Press Z to shot bullet and Q to quit."),
                 
                (12,"Get power ups. Kill robots. Press Enter to start.")]
        gfx.clear()
        for y,t in title:
            x = 40-len(t)//2
            q = y==1
            
            for c in t:
                gfx.draw(x,y,c,'g'+("!" if q else ""))
                x+= 1
    
    # Runs an interactive session of our game with the player until either
    # the player stops playing or an error occurs. Here, we pass input to the
    # world until we are told we don't need to anymore. If an error occurs, we
    # turn off graphics, print the traceback, and kill the program.
    def play(self):
        gfx.start()
        
        try:
            c = -1
            while c != "enter":
                self.display_title()
                c = gfx.get_input()
        
            while self.world.running:
                c = gfx.get_input()
                self.world.handle(c)
                self.world.draw()
                self.world.draw_gui()
        except:
            gfx.stop()  
            print(traceback.format_exc())
            sys.exit(-1)
        
        gfx.stop()

