from core import gfx
from core import log

# The ring function returns all of the tiles that make up the ring of radius
# 'r' around (x,y).
def ring(x,y,r):
    report = []
    odd = True if y % 2 == 1 else False
    
    # We start at 0 degrees, which is directly to the right, and then go
    # counter clockwise.
    x += r
    report.append((x,y))
    for i in range(r): #going up-left
        if not odd: x -= 1
        y -= 1
        report.append((x,y))
        odd = not odd
    for i in range(r): #going left
        x -= 1
        report.append((x,y))
    for i in range(r): #going down-left
        if not odd: x -= 1
        y += 1
        report.append((x,y))
        odd = not odd
    for i in range(r): #going down-right
        if odd: x += 1
        y += 1
        report.append((x,y))
        odd = not odd
    for i in range(r): #going right
        x += 1
        report.append((x,y))
    for i in range(r): #going up-right
        if odd: x += 1
        y -= 1
        report.append((x,y))
        odd = not odd
    
    # Return the report. Note that the 0-degree tile is at the beginning and
    # end of the list.
    return report


# Get the X,Y coordinates of the neighbor of x,y in direction d.
#   2 1    Returns None if no such direction.
#  3 @ 0
#   4 5
def direction(x, y, d):
    if d < 0 or d > 5: return None
    else: return ring(x,y,1)[d]


# 
def fov(x,y,r):
    report = [(x,y)]
    for i in range(r+1):
        report += ring(x,y,i)
    return report


# An entity is anything that exists in the world.
class Entity(object):
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y
        self.char = name[0]
    
    # Attempt to move 1 tile in a direction.
    def move(self, way):
        pos = direction(self.x, self.y, way)
        if pos: self.x, self.y = pos

        

# The World is our view into the tiled game world. Entities exist within the
# world and are located at x,y coordinates that represent tiles.
class World(object):
    def __init__(self):
        self.w = 20
        self.h = 20
        self.player = Entity("Player",4,4)
        self.entities = [self.player]
        self.player.char = "@"
    
    # Draws the world.
    def draw(self):
        gfx.clear()
        my_fov = fov(self.player.x,self.player.y,3)
        for y in range(self.h):
            odd = True if y % 2 == 1 else False
            for x in range(self.w):
                ax = x*2 + (1 if odd else 0)
            
                # For each tile that can be seen, determine what will be drawn
                # there.
                if (x,y) in my_fov:
                    empty = True
                    for e in self.entities:
                        if (e.x,e.y) == (x,y):
                            gfx.draw(ax,y,e.char)
                            empty = False
                    if empty:
                        gfx.draw(ax,y,".")

    # Handle input.
    def handle(self, c):
        if   c == "k": self.player.move(0)
        elif c == "i": self.player.move(1)
        elif c == "u": self.player.move(2)
        elif c == "h": self.player.move(3)
        elif c == "n": self.player.move(4)
        elif c == "m": self.player.move(5)

