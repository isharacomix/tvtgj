
import time


logfile = None
def log(s):
    global logfile
    if not logfile:
        logfile = open("log_%d"%time.time(),"w")
    logfile.write(s+"\n")


