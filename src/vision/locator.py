import numpy as np
import cv2
import json
import apriltag
from imutils.video import WebcamVideoStream
from math import atan2, asin, sin, cos,radians, sqrt
from scipy.signal import medfilt2d

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
        self.last = (False, None, None)
        self.pose_buff = []
        self.yaw_buff = []
        self.ret = True

    def get_worldPoints(self):
        return self.world_points

    """
        Helper Function for converting rotation matrix R to yaw/pitch/roll
    """
    def get_orientation(self, camera_matrix, R, t):
        """
        roll = atan2(-R[2][1], R[2][2])
        pitch = asin(R[2][0])
        yaw = atan2(-R[1][0], R[0][0])
        """
        proj = camera_matrix.dot(np.hstack((R, t)))
        rot = cv2.decomposeProjectionMatrix(proj)
        rot = rot[-1]
        print(rot, end ='-------------------------------\n')
        return rot[1], rot[0], rot[2]
    
    def calc_weight(self, p1, p2):
        max_weight = 150
        dist = np.linalg.norm(p1-p2)
        return max_weight/dist
        

    def locate(self, frame, buff):
        if self.c != 0 and self.c % buff == 0: 
            self.c = 0
            if self.pose_buff and self.yaw_buff:
                p = np.median(self.pose_buff, axis=0)
                y = np.median(self.yaw_buff)
                self.last = (self.ret, p, y)
                return self.ret, p, y
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
                
                weight = self.calc_weight(pose, self.world_points[tag_id][0])

                # Display yaw/pitch/roll and pose
            #    print("Tag: {}".format(tag_id))
                poses.append((pose, weight))
                yaw, pitch, roll = self.get_orientation(self.cameraMatrix, rot_mat, t)
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

        
