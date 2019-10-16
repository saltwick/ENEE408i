import threading 
from Threads import Arduino_Thread, Vision_Thread, Counter_Thread, Flask_Thread
from flask import Flask
 
app = Flask(__name__)
# Initialize threads
vision = Vision_Thread(False)
arduino = Arduino_Thread()

#f = Flask_Thread(app)

# Start Threads
arduino.start()
vision.start()
#f.setDaemon(True)
#f.start()
# Join threads
arduino.join()
vision.join()
print("All threads have finished")
