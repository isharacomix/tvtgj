
import time


logfile = None
is_logging = False
def log(s):
    global logfile
    global is_logging
    if is_logging:
        if not logfile:
            logfile = open("log_%d"%time.time(),"w")
        logfile.write(s+"\n")

def toggle(flag):
    global is_logging
    is_logging = True if flag else False

