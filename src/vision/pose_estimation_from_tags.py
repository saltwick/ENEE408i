import numpy as np
import cv2
import json
import apriltag
from imutils.video import WebcamVideoStream
from math import atan2, asin

"""
    Helper Function for converting rotation matrix R to yaw/pitch/roll
"""
def get_orientation(R):
    roll = atan2(-R[2][1], R[2][2])
    pitch = asin(R[2][0])
    yaw = atan2(-R[1][0], R[0][0])

    return yaw, pitch, roll

# Initialize apriltag detector
det = apriltag.Detector()

# Load camera data
with open('cameraParams.json', 'r') as f:
    data = json.load(f)

cameraMatrix =np.array(data['cameraMatrix'], dtype=np.float32)
distCoeffs = np.array(data['distCoeffs'], dtype=np.float32)

# Load world points
world_points = {}
with open('worldPoints.json', 'r') as f:
    data = json.load(f)

for k,v in data.items():
    world_points[int(k)] = np.array(v, dtype=np.float32).reshape((4,3,1))

# Video Loop
cap = WebcamVideoStream(src=0).start()
while True:
    frame = cap.read()
    # Use grayscale image for detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    res = det.detect(gray)
    
    for r in res:
        corners = r.corners
        tag_id = r.tag_id
        corners = np.array(corners, dtype=np.float32).reshape((4,2,1))
        # Draw circles on tags
        for c in corners:
            c = tuple([int(x) for x in c])
            frame = cv2.circle(frame, c, 5, (255,0,0), 1)
        # get rotation and translation vector using solvePnP
        r, rot, t = cv2.solvePnP(world_points[tag_id], corners, cameraMatrix, distCoeffs)
        # convert to rotation matrix
        rot_mat, _ = cv2.Rodrigues(rot)

        # Use rotation matrix to get pose = -R * t (matrix mul w/ @)
        R = rot_mat.transpose()
        pose = -R @ t

        # Display yaw/pitch/roll and pose
        print("Pose: ", pose)
        yaw, pitch, roll = get_orientation(R)
        print("Yaw: {} \n Pitch: {} \n Roll: {}".format(yaw,pitch,roll))

    # Display frame
    cv2.imshow('frame', frame)
    
    # Q to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
