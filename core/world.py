from core import gfx
from core import log



def ring(x,y,r):
    report = []
    odd = True if y % 2 == 1 else False
    
    # starting point, right, 0 degrees
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
        odd = not odd
        report.append((x,y))
    for i in range(r): #going down-right
        if odd: x += 1
        y += 1
        odd = not odd
        report.append((x,y))
    for i in range(r): #going right
        x += 1
        report.append((x,y))
    for i in range(r): #going up-right
        if odd: x += 1
        y -= 1
        report.append((x,y))
        odd = not odd

    #log.log("Trying to calculate neighbors for %d,%d"%(x,y))
    #log.log("Neighbors = [%s]"%(str(report)))
    
    return report

    
    


def view(x,y,r):
    report = []
    for i in range(r+1):
        report += ring(x,y,i)
    return report



class World(object):
    def __init__(self):
        self.w = 20
        self.h = 20
        self.player_x = 4
        self.player_y = 4
    
    # Draws the world
    def draw(self):
        gfx.clear()
        #log.log("DRAWING")
        my_neighbors = view(self.player_x,self.player_y,3)
        for y in range(self.h):
            odd = True if y % 2 == 1 else False
            for x in range(self.w):
                dx = x*2 + (1 if odd else 0)
            
                if (self.player_x,self.player_y) == (x,y):
                    gfx.draw(dx,y,"@")
                elif (x,y) in my_neighbors:
                    gfx.draw(dx,y,".")
        #log.log("DONE DRAWING\n\n")
        
        

