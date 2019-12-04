import numpy as np
import cv2
import time
import serial
from imutils.video import FPS, WebcamVideoStream
import threading
from threading import Lock
import apriltag
import json
from math import asin, atan2, sqrt
from flask import Flask, render_template
from ArduinoController import ArduinoController
import sys
sys.path.append('..')
from vision import Tracker
from vision import locator
from client import clientclass
from math import sin, cos, radians, atan2, degrees
#from multiprocessing import Process
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
        "MoveBackward": 0,
        "SlowDown": 0,
        "TurnLeft": 0,
        "TurnRight": 0,
        "Missing": 0
}
prev_controls = {
        "MoveForward": 0,
        "MoveBackward": 0,
        "SlowDown": 0,
        "TurnLeft": 0,
        "TurnRight": 0,
        "Missing": 0
}
SEND_LOCATION = True
POSE = {
    "x": np.array([100]),
    "y": np.array([100]),
    "heading": 0
}

camera_angle = 0
"""
Thread class for Arduino Control
"""
class Arduino_Thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    
    # Encode control dictionary to byte array
    def encode(self,controls):
        global camera_angle
        vals = [controls['MoveForward'], controls['MoveBackward'], controls['SlowDown'], controls['TurnLeft'], controls['TurnRight'], camera_angle + 70]
        
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

            #if self.controls_have_changed(controls, prev_controls):
            AController.send_message(self.encode(controls))


class Navigation_Thread(threading.Thread):
    def __init__(self, lock):
        threading.Thread.__init__(self)
        self.lock = lock
        self.speed = 27
        self.camera_angle = 0

    def dist(self, x1, y1, x2, y2):
        return sqrt((x2-x1)**2 + (y2-y1)**2) 

    def stop(self):
        #self.update_controls()
        for k in controls.keys():
            controls[k] = 0 

    def update_controls(self):
        global controls
        global prev_controls
        prev_controls['MoveForward'] = controls['MoveForward']
        prev_controls['MoveBackward'] = controls['MoveBackward']
        prev_controls['Missing'] = controls['Missing']
        prev_controls['TurnLeft'] = controls['TurnLeft']
        prev_controls['TurnRight'] = controls['TurnRight']

    def goto(self, x,y):
        global POSE
        global controls
        pX = POSE['x'].item()
        pY = POSE['y'].item()
        ang = POSE['heading']
        ang_buff = 15
        pos_buff = 1
        if x > pX:
            target_ang = 270
        if x < pX:
            target_ang = 90

        #print("Target angle is {}".format(target_ang))
        while not(target_ang - ang_buff < ang < target_ang+ang_buff):
        #    self.update_controls()
            #print(ang, target_ang-ang_buff, target_ang+ang_buff)
            ang = POSE['heading']
            controls['TurnLeft'] = self.speed
            time.sleep(0.5)
        #    self.update_controls()
            controls['TurnLeft'] = 0
            time.sleep(1.5)

        with self.lock:
            print("Facing target angle, move forwards")
        self.stop()
        time.sleep(1)

        while not (x-pos_buff <= pX <= x+pos_buff):
        #    self.update_controls()
            with self.lock:
                print(pX, x) 

            pX = POSE['x'].item()
            controls['MoveForward'] = self.speed

        with self.lock:
            print("Reached correct X")

        self.stop()
        time.sleep(1)

        ang = POSE['heading']
        target_ang = 0
        while not(target_ang - ang_buff < ang < target_ang+ang_buff):
        #    self.update_controls()
            print("Turn to {}".format(target_ang))
            ang = POSE['heading']
            controls['TurnLeft'] = self.speed
            time.sleep(0.5)
            controls['TurnLeft'] = 0
            time.sleep(1.5)

        with self.lock:
            print("Facing angle 0")
        self.stop()
        time.sleep(1)

        while not (y-pos_buff <= pY <= y+pos_buff):
        #    self.update_controls()
            pY = POSE['y'].item()

        #    self.update_controls()
            if y < pY:
                controls['MoveForward'] = self.speed
                controls['MoveBackward'] = 0
                print("Need to move forwards")
            elif y < pY:
                print("Need to move backwards")
                controls['MoveForward'] = 0
                controls['MoveBackward'] = self.speed

            time.sleep(2)

        # Reached correct position
        # Reset Controls
        self.stop()

        """
        turn and go

        target_ang = atan2(y-pY, x-pX)
        while not(target - ang_buff < radians(ang) < target + ang_buff):
            ang = POSE['heading']
            controls['TurnLeft'] = 50

        controls['TurnLeft'] = 0
        print(self.dist(pX, pY, x, y))        
        while self.dist(pX, pY, x,y) > pos_buff:
            pX = POSE['x']
            pY = POSE['y']
            controls['MoveForward'] = 50
        """ 

        with self.lock:
            print("Arrived at location {}".format((x,y)))

    def run(self):
        time.sleep(3)
        print("going to origin")
        self.goto(0,4)
        
        
"""
Thread class for April Tag Localizing

"""
class Location_Thread(threading.Thread):
    def __init__(self, lock):
        threading.Thread.__init__(self)
        self.cap = WebcamVideoStream(src=0).start()
        self.lock = lock
        self.loc = locator.Locator() 
        self.area_size = 160
        self.load_area()

    def create_area(self):
        hall_width = 32
        self.area = np.ones((self.area_size,self.area_size))*255
        # axis
        self.area = cv2.line(self.area,(self.area_size//2,0),
                (self.area_size//2,self.area_size), (0,255,0), 1)
        self.area = cv2.line(self.area, (0, self.area_size//2),
                (self.area_size,self.area_size//2), (0,255,0), 1)
        # Opposite hallway
        self.area = cv2.line(self.area, (0, self.area_size//2-hall_width), (self.area_size, self.area_size//2 - hall_width), (0,255,0), 2)
        # left wall
        self.area = cv2.line(self.area, (17, self.area_size), (17, self.area_size//2), (0,255,0), 2)
        # left hallway near wall
        self.area = cv2.line(self.area, (17, self.area_size//2), (0, self.area_size//2), (0,255,0), 2)
        # right wall
        self.area = cv2.line(self.area, (self.area_size-7, self.area_size), (self.area_size-7, self.area_size//2), (0,255,0), 2)
        # right hallway near wall
        self.area = cv2.line(self.area, (self.area_size-7, self.area_size//2), (self.area_size, self.area_size//2), (0,255,0), 2)
        # left side of door
        self.area = cv2.line(self.area, (self.area_size//2 - 63, self.area_size//2 + 10), (self.area_size//2-63 + 3, self.area_size//2 + 10), (0,255,0), 2)
        # right side of door
        self.area = cv2.line(self.area, (self.area_size//2-45, self.area_size//2 + 10), (self.area_size//2-45-3, self.area_size//2 + 10), (0,255,0), 2)
        # inner right wall
        self.area = cv2.line(self.area, (self.area_size//2+55, self.area_size//2+10), (self.area_size//2 + 55, self.area_size//2), (0,255,0), 2)
        self.area = cv2.line(self.area, (self.area_size//2+55, self.area_size//2+10), (self.area_size//2 + 73, self.area_size//2+10), (0,255,0), 2)
        # inner left wall
        self.area = cv2.line(self.area, (self.area_size//2 - 45, self.area_size//2 + 10), (self.area_size//2-45, self.area_size//2), (0,255,0), 2)
        # front wall
        self.area = cv2.line(self.area, (self.area_size//2 - 45, self.area_size//2), (self.area_size//2 + 55, self.area_size//2), (0,255,0), 2)


    def load_area(self):
        self.area = cv2.imread('map-scaled.png')
        self.clean_area = self.area.copy()

    def clear_area(self):
        self.area = self.clean_area

    def set_camera_angle(self,wp):
        global POSE
        pose = [POSE['x'].item(), POSE['y'].item()]
        ang = POSE['heading']
        points = list(wp.values())
        points = [x[0] for x in points]
        points = [[x[0].item(),x[2].item()] for x in points]
        points = sorted(points, key=lambda x: sum((np.array(x)-np.array(pose))**2))
       # print(ang)
        for p in points:
            dx = p[0] - pose[0]
            dy = p[1] - pose[1]
            cam_to_tag = degrees(atan2(dx,dy ))
            if cam_to_tag < 0:
                cam_to_tag += 360
            
            head = ang + 180
            t = head - cam_to_tag

            if -70 <= t <= 70:
       #         print("{} is the closest point in view of the camera".format(p))
#                print("dx: {} dy: {} cam_to_tag: {} heading: {} t: {}".format(dx,
            #        dy, cam_to_tag, ang, t))
                return camera_angle

        return 0


        
    def run(self):
        global HALT
        global controls
        global POSE
        global camera_angle
        mul = 4
        d = 30
        while True:
            frame = self.cap.read()
            wp = self.loc.get_worldPoints()
            camera_angle = self.set_camera_angle(wp) 
            ret, pose, yaw, heading = self.loc.locate(frame, 10)
            #print(heading)
            if ret:
               # print(degrees(yaw))
                #yaw = yaw - camera_angle
                h1 = (mul*pose[0] + mul*self.area_size//2, mul*pose[2] + mul*self.area_size//2)
                h2 = (h1[0] - d*sin(radians(yaw)), h1[1] - d*cos(radians(yaw)))
                h1 = tuple([int(x.item()) for x in h1])
                h2 = tuple([int(x.item()) for x in h2])
                self.area = cv2.circle(self.area, h1, 5, (255,0,0),2)
                self.area = cv2.arrowedLine(self.area, h1, h2,
                        (0,255,0), 2)
                POSE['x'] = pose[0]
                POSE['y'] = pose[2]
                POSE['heading'] = yaw
            

            # Display frame
            cv2.imshow('frame', frame)

            # Display map
            cv2.imshow('map', self.area)
           
            self.load_area()
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
Thread class for Chat Client

"""
class Client_Thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        print("Connecting to the chat server")
        # server IP
        IP = "10.104.84.250"
        self.client = clientclass.ChatClientClass("BIG_AL", IP)

    def run(self):
        time.sleep(3)
        while True:
            global POSE
            global HALT
            global SEND_LOCATION
            if HALT:
                print("Client Thread Exiting")
                break
            loc = [POSE['x'].item(), POSE['y'].item()]
            loc = [str(int(x)) for x in loc]
            if SEND_LOCATION:
                self.client.send(loc[0], loc[1])
                SEND_LOCATION = False

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
