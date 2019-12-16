import numpy as np
import cv2
import json
import apriltag
from imutils.video import WebcamVideoStream
from math import atan2, asin, sin, cos,radians, sqrt, degrees
import math
from scipy.signal import medfilt2d
import time
class MedianBuffer:

    def __init__(self, n):
        self.buffer = np.array([[0,0,0]]*n)
        self.buffer_length = n

    def push(self, x):
        self.buffer = np.append(self.buffer, x, axis=1)

    def pop(self):
        window = 3
        if len(self.buffer) > window:
            med = np.median(self.buffer[:,:window])
            self.buffer = self.buffer[:, 1:]
            return med
        elif len(self.buffer) == 0:
            return [0,0,0]
        else:
            return self.buffer[0]



class Locator:

    def __init__(self):
        # Initialize apriltag detector
        self.det = apriltag.Detector()
        self.c = 0
        # Load camera data
        with open('cameraParams.json', 'r') as f:
            data = json.load(f)

        self.cameraMatrix =np.array(data['cameraMatrix'], dtype=np.float32)
        self.distCoeffs = np.array(data['distCoeffs'], dtype=np.float32)

        # Load world points
        self.world_points = {}
        with open('worldPoints.json', 'r') as f:
            data = json.load(f)

        for k,v in data.items():
            self.world_points[int(k)] = np.array(v, dtype=np.float32).reshape((4,3,1))

        self.pose_buffer = MedianBuffer(10)
        self.last = (False, None, None, None)
        self.pose_buff = []
        self.yaw_buff = []
        self.ret = True
        self.heading = np.array([0,1,0])

    def get_worldPoints(self):
        return self.world_points

    """
        Helper Function for converting rotation matrix R to yaw/pitch/roll
    """
    def get_orientation(self, camera_matrix, R, t):
        """
        roll = atan2(-R[2][1], R[2][2])
        pitch = asin(R[2][0])
        """
        #yaw = atan2(-R[1][0], R[0][0])
        proj = camera_matrix.dot(np.hstack((R, t)))
        rot = cv2.decomposeProjectionMatrix(proj)
        rot = rot[-1]
        #print(rot, end ='-------------------------------\n')
        """
        if yaw < 0:
            yaw += math.pi

        return yaw
        """
        yaw = rot[1]

        """
        sy = math.sqrt(R[0][0] * R[0][0] + R[1][0]* R[1][0])
        singular = sy < 1e-6

        y = math.atan2(-R[2][0], math.sqrt((R[2][1])**2 + (R[2][2])**2))
        yaw = degrees(y)

        if (-R[2][0] < 0 and math.sqrt((R[2][1])**2 + (R[2][2])**2) < 0):
            yaw += 90
        elif (-R[2][0] > 0 and math.sqrt((R[2][1])**2 + (R[2][2])**2) < 0):
            yaw -=90

        print(yaw, -R[2][0], math.sqrt((R[2][1])**2 + (R[2][2])**2))
        """
        #yaw = degrees(y)
        #print(yaw, -R[2][0], sy)

        """
        normal = np.array([0,0,1])
        heading = R @ normal
        heading_normed = heading / np.linalg.norm(heading)
        angle = np.dot(normal, heading_normed)
        axis = np.cross(normal, heading_normed)
        
        x = axis[0]
        y = axis[1]
        z = axis[2]

        yaw = math.asin(axis[0] * axis[1] * (1 - math.cos(angle)) + axis[2] * math.sin(angle))
        heading = atan2(y * sin(angle)- x * z * (1 - cos(angle)) , 1 - (y**2 + z**2 ) * (1 - cos(angle)))
        bank = atan2(x * sin(angle)-y * z * (1 - cos(angle)) , 1 - (x**2 + z**2) * (1 - cos(angle)))
        print(degrees(heading), degrees(yaw), degrees(bank))
        """
        return yaw
   
    # Calculate weight function based on distance between points
    def calc_weight(self, p1, p2):
        max_weight = 150
        dist = np.linalg.norm(p1-p2)
        return max_weight/dist
        
    # Locate a tag in a frame and return radius, x,y, worldpoints 
    def find_tag(self, frame, tag_id):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        res = self.det.detect(gray)
        tagObject = None
        for r in res:
            if r.tag_id == tag_id:
                tagObject = r

        if tagObject:

            corners = np.array(tagObject.corners, dtype=np.float32).reshape((4, 2, 1))
            cornersList = []
            for c in corners:
                cornersList.append([int(x) for x in c])
            cornersList = np.array(cornersList, dtype=np.int32)
            ((x, y), radius) = cv2.minEnclosingCircle(cornersList)
            M = cv2.moments(cornersList)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            filteredPtsRadius = [radius]
            filteredPtsX = [center[0]]
            filteredPtsY = [center[1]]   
            return filteredPtsRadius[0], filteredPtsX[0], filteredPtsY[0], self.world_points[tag_id]

        else:
            return None, None, None, []

    # Return robot position and heading based on April Tag localization
    def locate(self, frame, buff):
        tags = [] 
        if self.c != 0 and self.c % buff == 0: 
            self.c = 0
            if self.pose_buff and self.yaw_buff:
                p = np.median(self.pose_buff, axis=0)
                y = np.median(self.yaw_buff)

                self.last = (self.ret, p, y, self.heading)
                return self.ret, p, y, self.heading
            else:
                return self.last
        else:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            res = self.det.detect(gray)
            poses = [] 
            yaws = []
            avg_yaw = avg_pose = None
            if not res:
                return self.last

            for r in res:
                corners = r.corners
                tag_id = r.tag_id
                if tag_id not in self.world_points.keys():
                    return self.last

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
                self.heading = -R @ self.heading
                weight = self.calc_weight(pose, self.world_points[tag_id][0])

                # Display yaw/pitch/roll and pose
            #    print("Tag: {}".format(tag_id))
                poses.append((pose, weight))
                yaw = self.get_orientation(self.cameraMatrix, R, t)
                yaws.append((yaw, weight))
        #        print("Yaw: {} \n Pitch: {} \n Roll: {}".format(yaw,pitch,roll))
             
            # Average poses and display on a map
            if len(poses) > 0:
                avg_pose = sum([x*y for x,y in poses]) / sum([x[1] for x in poses])
                # For Displaying
                #for i,c in enumerate(avg_pose):
                #    avg_pose[i] = list(map(lambda x: x*4, c))
            else:
                self.ret &= False

        #        print("Pose: ", avg_pose)
            p1 = p2 = None

            if len(yaws) > 0:
                avg_yaw = sum([x*y for x,y in yaws]) / sum([x[1] for x in yaws])
                #print(avg_yaw, p1,p2)
            else:
                self.ret &= False
            
            self.pose_buff.append(avg_pose)
            self.yaw_buff.append(avg_yaw)
            if len(self.pose_buff) > buff:
                self.pose_buff.pop(0)
            if len(self.yaw_buff) > buff:
                self.yaw_buff.pop(0)


            self.c += 1
            return self.last

        
