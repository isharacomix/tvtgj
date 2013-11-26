from core import gfx
from core import log

import random


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

# This returns the distance between two tiles.
# Algorithm: First, walk down/diagonally until at the same row. Then
# calculate horizontal distance.
def distance( pos1, pos2 ):
    x1,y1 = pos1
    x2,y2 = pos2
    if x1 > x2:
        x1,y1 = pos2
        x2,y2 = pos1
      
    # First, go diagonally and left. pos2 is guaranteed to be to the right
    # of pos1, which helps us deal with the assumptions of how to handle odd
    # rows.
    dist = 0
    odd = True if y2 % 2 == 1 else False
    dy = 1 if y1 > y2 else -1
    while y1 != y2:
        if x1 < x2:
            if not odd: x2 -= 1
        y2 += dy
        odd = not odd
        dist += 1
    dist += x2-x1
    
    return dist

# This returns the angle between two tiles.
def angle( pos1, pos2 ):
    if pos1 == pos2:
        return None
    
    x1,y1 = pos1
    x2,y2 = pos2
    
    # Basically create a ring around pos1, and then find the position
    # in the ring of pos2.
    r = distance(pos1,pos2)
    orig = ring(x1,y1,r)
    i = orig.index(pos2)
    angle = i * 360.0 / (r*6)
    
    return angle


# This takes the definition of an arc (a set of (st,en) tuples) and
# breaks them at angle by putting a gap of size degrees in the arc.
def split_arc(arc, angle, size):
    report = []
    for (st,en) in arc:
        if st-size <= angle and angle <= en+size:
            s1,e1 = st,angle-size
            s2,e2 = angle+size,en
            
            # Does not work on the 0,360 split, or for certain boundary
            # cases.
            
            if s1 < e1: report.append((s1,e1))
            if s2 < e2: report.append((s2,e2))
        else:
            report.append((st,en))
            
    return report


# Get the X,Y coordinates of the neighbor of x,y in direction d.
#   2 1    Returns None if no such direction.
#  3 @ 0
#   4 5
def direction(x, y, d):
    if d < 0 or d > 5: return None
    else: return ring(x,y,1)[d]


# The arc method takes a list of tuples containing "start_degree, end_degree"
# pairs. It returns the sublist of a complete ring that fits within the starts
# and ends.
def arc(x, y, r, endpoints):
    if r < 1:
        return [(x,y)]
    orig = ring(x,y,r)
    report = []
    for (st, en) in endpoints:
        chunk_size = 360.0 / (r*6)
        h_chunk = chunk_size / 2
        while st < 0:
            st += 360
            en += 360
        if en-st > 359:
            return orig
        elif en-st > h_chunk:
            st_i = int(1.0*(st+h_chunk) / chunk_size) % (r*6)
            en_i = int(1.0*(en+h_chunk) / chunk_size) % (r*6)
            if st_i <= en_i:
                report += orig[st_i:en_i+1]
            else:
                report += orig[st_i:]
                report += orig[:en_i+1]
    return report


# An entity is anything that exists in the world.
class Entity(object):
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y
        self.char = name[0]
        self.target = None
        self.angle = 0
        self.lense = 30
    
    # Attempt to move 1 tile in a direction.
    def move(self, way, world):
        pos = direction(self.x, self.y, way)
        if pos and world.is_free(*pos): self.x, self.y = pos

    # Attempt to move the target.
    def target_move(self, way):
        if not self.target:
            self.target = self.x,self.y
        x,y = self.target
        pos = direction(x,y,way)
        if pos: self.target = pos
        

# The World is our view into the tiled game world. Entities exist within the
# world and are located at x,y coordinates that represent tiles.
class World(object):
    def __init__(self):
        self.w = 20
        self.h = 20
        self.map = ["."*self.w]*self.h
        self.player = Entity("Player",15,5)
        self.entities = [self.player]
        self.player.char = "@"
        
        
        for a in range(self.h):
            for b in range(self.w):
                #if random.randint(0,100) < 5:
                if a == 10 or b == 10:
                    self.map[a] = self.map[a][:b]+"#"+self.map[a][b+1:]
    
    # Returns true if a square is free.
    def is_free(self, x, y):
        if x < 0 or y < 0 or x >= self.w or y >= self.h:
            return False
        if self.map[y][x] != "#":
            return True
        return False
    
    # Do field of vision calculations in the world. Causes breaks in
    # opaque tiles. Normally goes in all directions, but you can constrain it.
    def fov(self,x,y,r,angles=[(0,360)]):
        report = [(x,y)]
        for i in range(1,r+1):
            view = arc(x,y,i,angles)
            for (ox,oy) in view:
                if not self.is_free(ox,oy):
                    theta = angle((x,y),(ox,oy))
                    angles = split_arc(angles, theta, 360./(i*6))
            report += view
        return report
    
    # Draws the world.
    def draw(self):
        gfx.clear()
        my_fov = self.fov(self.player.x,self.player.y,10,[(self.player.angle-self.player.lense,self.player.angle+self.player.lense)])
        #my_fov = self.fov(self.player.x,self.player.y,10)
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
                        c = self.map[y][x]
                        gfx.draw(ax,y,c,"g" if c == "." else "y")
                if self.player.target == (x,y):
                    gfx.draw(ax-1,y,"[")
                    gfx.draw(ax+1,y,"]")

    # Handle input.
    def handle(self, c):
        if   c == "k": self.player.move(0,self)
        elif c == "i": self.player.move(1,self)
        elif c == "u": self.player.move(2,self)
        elif c == "h": self.player.move(3,self)
        elif c == "n": self.player.move(4,self)
        elif c == "m": self.player.move(5,self)
        elif c == "f": self.player.target_move(0)
        elif c == "r": self.player.target_move(1)
        elif c == "e": self.player.target_move(2)
        elif c == "s": self.player.target_move(3)
        elif c == "x": self.player.target_move(4)
        elif c == "c": self.player.target_move(5)
        elif c == "d": self.player.target = None
        elif c == "left": self.player.angle = (self.player.angle+10)%360
        elif c == "right": self.player.angle = (self.player.angle-10)%360
        elif c == "up" and self.player.lense < 100: self.player.lense += 5
        elif c == "down" and self.player.lense > 0: self.player.lense -= 5
        
