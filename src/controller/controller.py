import threading 
from threading import Lock
from Threads import Arduino_Thread, Vision_Thread, Counter_Thread, Flask_Thread, Location_Thread
from flask import Flask
 
app = Flask(__name__)
lock = Lock()
# Initialize threads
#vision = Vision_Thread(False)
#arduino = Arduino_Thread()
local = Location_Thread(lock)
#f = Flask_Thread(app)

# Start Threads
#arduino.start()
#vision.start()
local.start()
#f.setDaemon(True)
#f.start()
# Join threads
#arduino.join()
#vision.join()
local.join()
print("All threads have finished")
