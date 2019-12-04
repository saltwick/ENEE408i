import threading 
from threading import Lock
from Threads import Arduino_Thread, Vision_Thread, Counter_Thread, Flask_Thread, Location_Thread, Navigation_Thread, Client_Thread
from flask import Flask
import multiprocessing
lock = Lock()
# Initialize threads
#vision = Vision_Thread(False)
arduino = Arduino_Thread()
local = Location_Thread(lock)
navigate = Navigation_Thread(lock)
#comms = Client_Thread()
f = Flask_Thread()

# Start Threads
arduino.start()
navigate.start()
#vision.start()
local.start()
f.setDaemon(True)

#comms.start()
#f.start()
# Join threads
alexa = Flask_Thread()

alexa.start()

alexa.join()
arduino.join()
navigate.join()
#vision.join()
local.join()
#comms.join()
print("All threads have finished")


