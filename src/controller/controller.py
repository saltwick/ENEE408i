import threading 
from Threads import Arduino_Thread, Vision_Thread, Counter_Thread, Flask_Thread
from flask import Flask

app = Flask(__name__)
# Initialize threads
vision = Vision_Thread(False)
counter = Counter_Thread()
arduino = Arduino_Thread()

#f = Flask_Thread(app)

# Start Threads
arduino.start()
vision.start()
counter.start()
#f.setDaemon(True)
#f.start()
# Join threads
arduino.join()
vision.join()
counter.join()
print("All threads have finished")
