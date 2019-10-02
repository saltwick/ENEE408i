import threading 
from Threads import Arduino_Thread, Vision_Thread, Counter_Thread


# Initialize threads
vision = Vision_Thread(True)
counter = Counter_Thread()
arduino = Arduino_Thread()

# Start Threads
arduino.start()
vision.start()
counter.start()

# Join threads
arduino.join()
vision.join()
counter.join()

print("All threads have finished")
