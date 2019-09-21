import threading 
import numpy as np
import cv2
import time
import serial
from imutils.video import FPS, WebcamVideoStream

from ArduinoController import ArduinoController
import sys
sys.path.append('..')
from vision import Tracker

# Intialize Connection to Arduino
AController = ArduinoController('device', 9600)
count = 0
HALT = False
change_controls = False

# Control structure that gets sent to Arduino
controls = {
        "MoveForward": 0,
        "SpeedUp": 0,
        "SlowDown": 0,
        "TurnLeft": 0,
        "TurnRight": 0,
        "Missing": 0
}

# Encode control dictionary to byte array
def encode(controls):
    vals = list(controls.values())
    data = bytearray(vals)
    return data

"""
Thread class for Arduino Control
"""
class Arduino_Thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    

    def run(self):
        global HALT
        global count
        global controls
        global change_controls
        global AController 

        #AController.start()
        while True:
            if HALT:
                print("Arduino Controller Exiting")
                break

            AController.send_message(encode(controls))


"""
Thread class for Vision System
"""
class Vision_Thread(threading.Thread):
    def __init__(self,debug):
        threading.Thread.__init__(self)
        self.cap = WebcamVideoStream(src=0).start()
        self.tracker = Tracker.Tracker(0.7)
        self.fps = FPS().start()
        self.tracker_width = 100
        self.debug = debug

    def run(self):
        global count
        global HALT
        global controls
       
        # Webcam recording loop
        while True:
            frame = self.cap.read() 
            # Get a copy of the current frame if we want to show the turning overlay
            if self.debug: overlay = frame.copy()
            height, width, _ = frame.shape
            centerX = int(width/2)
            box= self.tracker.track(frame)

            # If someone was detected
            if box:
                # Move forwards
                controls['MoveForward'] = 1
                (x,y,w,h) = box

                # Draw bounding box
                cv2.rectangle(frame, (int(x), int(y)), (int(x+w), int(y+h)), (0,255,0),2)

                # Get person center
                cX = int(x+(w/2))
                cY = int(y+(h/2))
                cv2.circle(frame, (cX,cY) , 2, (0,255,0), 2)
                
                # Modify turn signal
                if cX < centerX - self.tracker_width:
                    dX = int(((centerX - cX)/(width/2))*150)
                    controls['TurnLeft'] = dX
                elif cX > centerX + self.tracker_width :
                    dX = int(((cX - centerX)/(width))*150)
                    controls['TurnRight'] = dX
                else:
                    dX = 0
                    controls['TurnLeft'] = dX
                    controls['TurnRight'] = dX
            # No person - set missing and stop
            else:
                controls['Missing'] = 1
                controls['MoveForward'] = 0

            # Display turning overlay if wanted
            if self.debug: 
                if cX > centerX+self.tracker_width:
                    print("Turn Right by {}".format(dX))
                    cv2.rectangle(overlay, (centerX, 0), (centerX+self.tracker_width, height), 
                            (0,255,0), -1)
                elif cX < centerX - self.tracker_width:
                    print("Turn Left by {}".format(dX))
                    cv2.rectangle(overlay, (centerX-self.tracker_width, 0), (centerX, height),
                            (0,255,0), -1)
                cv2.addWeighted(overlay, 0.5, frame, 1-0.5, 0, frame)

            # Always display tracking frame
            cv2.line(frame, (centerX-self.tracker_width, 0), (centerX-self.tracker_width, height),
                    (0,0,255),2)
            cv2.line(frame, (centerX+self.tracker_width, 0), (centerX+self.tracker_width, height),
                    (0,0,255),2)

            # Display current frame
            cv2.imshow('frame', frame)

            self.fps.update()

            # Q key ends vision thread
            if cv2.waitKey(1) & 0xFF == ord('q') or HALT:
                break

        self.fps.stop()
        cv2.destroyAllWindows()
        HALT = True
        print('Video thread exiting -- FPS= {}'.format(self.fps.fps()))

"""
Thread class for testing a counter
"""
class Counter_Thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global count
        global HALT
        global controls
        while True:
            
            if HALT:
                print("Counter Thread Exiting")
                break

            count += 1
            time.sleep(1)

# Initialize threads
vision = Vision_Thread(False)
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
