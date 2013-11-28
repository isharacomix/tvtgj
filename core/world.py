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
        if st < en:
            st_i = int(1.0*(st+h_chunk) / chunk_size) % (r*6)
            en_i = int(1.0*(en+h_chunk) / chunk_size) % (r*6)
            if st_i <= en_i:
                report += orig[st_i:en_i+1]
            else:
                report += orig[st_i:]
                report += orig[:en_i+1]
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

# Get the point on the angle that is 'r' away from x,y. Essentially the
# opposite of angle.
def apoint(x,y,r,theta):
    if r == 0:
        return (x,y)
    while theta < 0:
        theta += 360
    orig = ring(x,y,r)
    chunk_size = 360.0 / (r*6)
    h_chunk = chunk_size / 2
    i = int(1.0*(theta+h_chunk) / chunk_size) % (r*6)
    return orig[i]

# Return a line of points from x,y to apoint(r,theta).
def aline(x,y,r,theta):
    report = []
    for i in range(1,r+1):
        report.append( apoint(x,y,i,theta) )
    return report

# Version of "aline" that let's you enter two x,y points.
def line(pos1,pos2):
    return aline(pos1[0],pos1[1],distance(pos1,pos2),angle(pos1,pos2))


# This takes the definition of an arc (a set of (st,en) tuples) and
# breaks them at angle by putting a gap of size degrees in the arc.
def split_arc(arc, angle, size):
    report = []
    arc2 = []
    
    # Normalize any endpoints that aren't in 0 to 360.
    for (st,en) in arc:
        while st < 0:
            st += 360
            en += 360
        while st > 360:
            st -= 360
        
        if en > 360:
            arc2.append((st,360))
            while en > 360:
                en-=360
            arc2.append((0, en))
        else:
            arc2.append((st,en))
    
    # Now break all of the arcs into size on either side of angle.
    for (st,en) in arc2:
        if st-size <= angle and angle <= en+size:
            s1,e1 = st,angle-size
            s2,e2 = angle+size,en
            
            if e1-s1 > 5: report.append((s1,e1))
            if e2-s2 > 5: report.append((s2,e2))
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
        self.hp = 5
        self.init = 0
    
    # Attempt to move 1 tile in a direction.
    def move(self, way, world):
        pos = direction(self.x, self.y, way)
        if pos and world.is_free(*pos):
            if not self.target: self.angle = angle((self.x,self.y),pos)
            self.x, self.y = pos
            self.init -= 5

    # Attempt to move the target.
    def target_move(self, way):
        if not self.target:
            self.target = self.x,self.y
        x,y = self.target
        pos = direction(x,y,way)
        if pos: self.target = pos
        self.init -= 1
    
    # Try to do something intelligent and fail.
    def ai(self, world):
        self.init -= 1
        if self.hp > 0:
            my_fov = world.fov(self.x,self.y,10,[(self.angle-self.lense,self.angle+self.lense)])
            foundem = False
            for (x,y) in my_fov:
                if (x,y) == (world.player.x,world.player.y) and world.player.hp > 0:
                    self.target = x,y
                    foundem = True
            if foundem:
                self.fire(world)
            else:
                self.move(random.randint(0,6), world)
    
    # Here we try to fire in the direction of the target.
    def fire(self, world):
        if self.target:
            error = random.randint(0,30)-15
            world.bullet_anim = aline(self.x,self.y,
                             distance((self.x,self.y),self.target),
                             error+angle((self.x,self.y),self.target))
            self.init -= 4
            world.gui_log("BANG!")
            

# The World is our view into the tiled game world. Entities exist within the
# world and are located at x,y coordinates that represent tiles.
class World(object):
    def __init__(self):
        self.w = 40
        self.h = 40
        self.camera = 0,0
        self.map = ["."*self.w]*self.h
        self.player = Entity("Player",15,5)
        self.entities = [self.player]
        self.player.char = "@"
        self.bullet_anim = []
        self.anim_tick = 0
        self.anim_speed = 30
        self.turn = 0
        self.log = ["May the best @ win!"]
        
        for a in range(self.h):
            for b in range(self.w):
                if random.randint(0,100) < 5:
                #if a == 10 or b == 10:
                    self.map[a] = self.map[a][:b]+"#"+self.map[a][b+1:]
        for a in range(4):
            e = Entity("Bad Guy",random.randint(5,15),random.randint(5,15))
            e.char = "@"
            self.entities.append(e)
    
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
                    angles = split_arc(angles, theta, 180./(i*6))
            report += view
        return report
    
    # Draws the world.
    def draw(self, cw=20, ch=20, vx=0, vy=0):
        cx,cy = self.camera 
        dx,dy = self.player.x-cx, self.player.y-cy
        if dx > 15 or dx < 5:
            cx = self.player.x - cw/2
        if dy > 15 or dy < 5:
            cy = self.player.y - ch/2
        self.camera = cx,cy
        
        self.anim_tick = (self.anim_tick + 1)%self.anim_speed
        if self.anim_tick == 0:
            if len(self.bullet_anim)>0:
                x,y = self.bullet_anim.pop(0)
                if not self.is_free(x,y):
                    self.bullet_anim = []
                for e in self.entities:
                    if (e.x,e.y) == (x,y):
                        e.hp -= 1
                        if e is self.player:
                            self.gui_log("I'm hit!")
                        if e.hp < 1:
                            e.char = "%"
                            self.gui_log("%s has died. :("%(e.name))
                        self.bullet_anim = []
        
        gfx.clear()
        if self.player.target:
            a = angle((self.player.x,self.player.y),self.player.target)
            if a is not None: self.player.angle = a
        my_fov = self.fov(self.player.x,self.player.y,10,[(self.player.angle-self.player.lense,self.player.angle+self.player.lense)])
        #my_fov = self.fov(self.player.x,self.player.y,10)
        #my_fov = []
        #for a in range(self.w):
        #    for b in range(self.h):
        #        my_fov.append((a,b))
        lineee = []
        if self.player.target:
            lineee = line((self.player.x,self.player.y),self.player.target)
        all_fovs = {}
        for e in self.entities:
            all_fovs[e] = self.fov(e.x,e.y,10,[(e.angle-e.lense,e.angle+e.lense)])
        for y in range(self.h):
            odd = True if y % 2 == 1 else False
            for x in range(self.w):
                if not(x >= cx and x < cx+cw and y >= cy and y < cy+ch):
                    continue
            
            
                ax = (x-cx+vx)*2 + (1 if odd else 0)
                ay = (y-cy+vy)
            
                # For each tile that can be seen, determine what will be drawn
                # there.
                if (x,y) in my_fov:
                    empty = True
                    for e in self.entities:
                        if (e.x,e.y) == (x,y):
                            gfx.draw(ax,ay,e.char,"b!" if e is self.player else "r!")
                            empty = False
                    if empty:
                        c = self.map[y][x]
                        gfx.draw(ax,ay,c,"g" if c == "." else "y")
                    if len(self.bullet_anim)>0 and self.bullet_anim[0] == (x,y):
                        gfx.draw(ax,ay,"*",'r')
                else:
                    for e in self.entities:
                        if (e is not self.player and (e.x,e.y)==(x,y) and
                            (self.player.x,self.player.y) in all_fovs[e]):
                                gfx.draw(ax,ay,"\"","r!")
                if self.player.target == (x,y):
                    gfx.draw(ax-1,ay,"[")
                    gfx.draw(ax+1,ay,"]")


    # Draw the datalog.
    def draw_gui(self, vx=41, vy=0, vw=38, vh=20 ):
        x = vx
        for c in "Robot Battle":
            gfx.draw(x,vy,c) 
            x += 1
        x = vx
        for c in "Your HP: %d"%self.player.hp:
            gfx.draw(x,vy+1,c)
            x += 1
    
    
        printy = self.log[-min(vh-3,len(self.log)):]
        y = vy+3
        for p in printy:
            x = vx
            for c in p[:vw]:
                gfx.draw(x,y,c)
                x += 1
            y += 1
    
    def gui_log(self, s):
        self.log.append(s)
    
    # Handle input.
    def handle(self, c):
        if len(self.bullet_anim) > 0:
            return #no movement during animation
        
        # Check init.
        current = self.entities[self.turn]
        if current.init < 0:
            self.turn = (self.turn+1)%len(self.entities)
            if self.turn == 0:
                for e in self.entities:
                    e.init += 10
                return
        
        
        if current is not self.player:
            current.ai(self)
            return
        
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
        elif c == "left": self.player.angle = (self.player.angle+5)%360 ; self.player.init -= 2
        elif c == "right": self.player.angle = (self.player.angle-5)%360 ; self.player.init -= 2
        elif c == "up" and self.player.lense < 100: self.player.lense += 1
        elif c == "down" and self.player.lense > 0: self.player.lense -= 1
        elif c == "z": self.player.fire(self)
        
        elif c == "1": self.gui_log("Hello!")
        elif c == "2": self.gui_log("Goodbye!")
        
        #if moved: self.turn = (self.turn+1)%len(self.entities)
        
        # Debug. Logs everything that occurs in a single frame.
        log.toggle( c == 'p' )
        
