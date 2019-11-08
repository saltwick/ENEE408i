import numpy as np
import cv2
import time
import serial
from imutils.video import FPS, WebcamVideoStream
import threading
from threading import Lock
import apriltag
import json
from math import asin, atan2
from flask import Flask, render_template
from ArduinoController import ArduinoController
import sys
sys.path.append('..')
from vision import Tracker
#from flask_ask import Ask, statement, question

# Intialize Connection to Arduino
AController = ArduinoController('/dev/ttyACM0', 38400)
count = 0
HALT = False
change_controls = False
follow_me = True
# Control structure that gets sent to Arduino
controls = {
        "MoveForward": 0,
        "SpeedUp": 0,
        "SlowDown": 0,
        "TurnLeft": 0,
        "TurnRight": 0,
        "Missing": 0
}
prev_controls = {
        "MoveForward": 0,
        "SpeedUp": 0,
        "SlowDown": 0,
        "TurnLeft": 0,
        "TurnRight": 0,
        "Missing": 0
}
"""
Thread class for Arduino Control
"""
class Arduino_Thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    
    # Encode control dictionary to byte array
    def encode(self,controls):
        vals = [controls['MoveForward'], controls['SpeedUp'], controls['SlowDown'], controls['TurnLeft'], controls['TurnRight'], controls['Missing']]
        
        data = vals
        return data

    def controls_have_changed(self, controls, prev_controls):
        for k,v in controls.items():
            if controls[k] !=  prev_controls[k]:
                return True
        return False
    def run(self):
        global HALT
        global count
        global controls
        global change_controls
        global AController 
        global prev_controls
        AController.start()
        while True:
            if HALT:
                print("Arduino Controller Exiting")
                break
            time.sleep(.2) 

            if self.controls_have_changed(controls, prev_controls):
                AController.send_message(self.encode(controls))



"""
Thread class for April Tag Localizing

"""
class Location_Thread(threading.Thread):
    def __init__(self, lock):
        threading.Thread.__init__(self)
        self.cap = WebcamVideoStream(src=0).start()
        self.det = apriltag.Detector()
        self.lock = lock
        # Load camera data
        with open('../vision/cameraParams.json', 'r') as f:
            data = json.load(f)

        self.cameraMatrix =np.array(data['cameraMatrix'], dtype=np.float32)
        self.distCoeffs = np.array(data['distCoeffs'], dtype=np.float32)

        # Load world points
        self.world_points = {}
        with open('../vision/worldPoints.json', 'r') as f:
            data = json.load(f)

        for k,v in data.items():
            self.world_points[int(k)] = np.array(v, dtype=np.float32).reshape((4,3,1))

    def get_orientation(self,R):
        roll = atan2(-R[2][1], R[2][2])
        pitch = asin(R[2][0])
        yaw = atan2(-R[1][0], R[0][0])

        return yaw, pitch, roll
    
    def run(self):
        global HALT
        while True:
            frame = self.cap.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            res = self.det.detect(gray)

            for r in res:
                corners = r.corners
                tag_id = r.tag_id
                corners = np.array(corners, dtype=np.float32).reshape((4,2,1))
                # Draw circles on tags
                for c in corners:
                    c = tuple([int(x) for x in c])
                    frame = cv2.circle(frame, c, 5, (255,0,0), 1)
                # get rotation and translation vector using solvePnP
                r, rot, t = cv2.solvePnP(self.world_points[tag_id], corners, self.cameraMatrix, self.distCoeffs)
                # convert to rotation matrix
                rot_mat, _ = cv2.Rodrigues(rot)

                # Use rotation matrix to get pose = -R * t (matrix mul w/ @)
                R = rot_mat.transpose()
                pose = -R @ t

                with self.lock:
                    # Display yaw/pitch/roll and pose
                    print("Pose: ", pose)
                    yaw, pitch, roll = self.get_orientation(R)
                    print("Yaw: {} \n Pitch: {} \n Roll: {}".format(yaw,pitch,roll))

            # Display frame
            cv2.imshow('frame', frame)
            
            # Q to quit
            if cv2.waitKey(1) & 0xFF == ord('q') or HALT:
                break
        HALT = True
        cv2.destroyAllWindows()

"""
Thread class for Vision System
"""
class Vision_Thread(threading.Thread):
    def __init__(self,debug):
        threading.Thread.__init__(self)
        self.cap = WebcamVideoStream(src=0).start()
        self.tracker = Tracker.Tracker(0.8)
        self.fps = FPS().start()
        self.tracker_width = 100
        self.debug = debug
        self.initBB = None

    def run(self):
        global count
        global HALT
        global controls
        global follow_me
        
        while (not follow_me):
            pass
        
        self.initBB = self.tracker.initialize(self.cap.read()) 
        if (self.initBB):
            print("Target Acquired")
        # Webcam recording loop
        while True:
            frame = self.cap.read() 
            # Get a copy of the current frame if we want to show the turning overlay
            if self.debug: overlay = frame.copy()
            height, width, _ = frame.shape
            centerX = int(width/2)
            box= self.tracker.track(frame, self.initBB)

            # If someone was detected
            if box:
                # Move forwards
                prev_controls['MoveForward'] = controls['MoveForward']
                prev_controls['Missing'] = controls['Missing']
                prev_controls['TurnLeft'] = controls['TurnLeft']
                prev_controls['TurnRight'] = controls['TurnRight']

                controls['MoveForward'] = 1
                controls['Missing'] = 0
                (x,y,w,h) = box

                # Draw bounding box
                cv2.rectangle(frame, (int(x), int(y)), (int(x+w), int(y+h)), (0,255,0),2)

                # Get person center
                cX = int(x+(w/2))
                cY = int(y+(h/2))
                cv2.circle(frame, (cX,cY) , 2, (0,255,0), 2)
                
                # Modify turn signal
                if cX < centerX - self.tracker_width:
                    dX = (centerX-self.tracker_width - cX)/(width/2 - self.tracker_width)
                    dX = min(255,int(dX * 255))
                    controls['TurnLeft'] = dX
                    controls['TurnRight'] = 0
                elif cX > centerX + self.tracker_width :
                    dX = ((cX - centerX - self.tracker_width)/ (width/2 - self.tracker_width))
                    dX = min(255, int(dX * 255))
                    controls['TurnRight'] = dX
                    controls['TurnLeft'] = 0
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
	
            elif cv2.waitKey(1) & 255 == ord('i'):
               self.initBB = None	
               self.initBB = self.tracker.initialize(self.cap.read()) 
               if (self.initBB):
                 print("Target Acquired")
               else:
                 print("No target Found")

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

"""
Thread class for Flask Server
"""
class Flask_Thread(threading.Thread):

    def home(self):
        return 'hi'

    def __init__(self, app):
        threading.Thread.__init__(self)
        self.app = app
        self.app.add_url_rule('/', 'home', view_func=self.home)
        # INIT FLASK SERVER HERE



    # DEFINE OTHER FUNCTIONS FOR INTENTS HERE
    def run(self):
        self.app.run(debug=False, host='0.0.0.0')   
        # START FLASK SERVER HERE
"""
    @ask.launch
    def launched():
        return question("Yo. I'm Big Al. If you need some kneecaps broken, I'm your man").reprompt(
        "Give me a job or let me watch the Yanks sweep the Sox")


    @ask.intent('AMAZON.FallbackIntent')
    def default():
        return question("Big Al don't know what you mean. Do you want me to break some kneecaps?").reprompt(
            "Give me a job or let me watch the Yanks sweep the Sox")


    @ask.intent('FollowIntent')
    def followMe(command):
        follow_me=True
        return question("Big Al is on the prowl").reprompt(
        "How much longer until I take care of this guy for good?")

"""
