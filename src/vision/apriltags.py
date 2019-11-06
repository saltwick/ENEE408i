import apriltag
import cv2
from imutils.video import WebcamVideoStream
import time
import numpy as np
import json

with open('worldPoints.json', 'r') as f:
    data = json.load(f)

world_points = {}
for k,v in data.items():
    world_points[int(k)] = np.array(v).reshape((4,3,1))

with open('cameraParams.json', 'r') as f:
    data = json.load(f)

cameraMatrix = np.ascontiguousarray(np.array(data['cameraMatrix'], dtype=np.float32))
distCoeffs = np.ascontiguousarray(np.array(data['distCoeffs'], dtype=np.float32).reshape((5,1)))

"""
objectPoints = np.random.random((10,3,1))
print(world_points, type(world_points), world_points.shape)
print(objectPoints, type(objectPoints), objectPoints.shape)
imagePoints = np.random.random((10,2,1))

#print(cv2.solvePnP(world_points, imagePoints, cameraMatrix, distCoeffs))

"""
cap = WebcamVideoStream(src=0).start()

detector = apriltag.Detector()

time.sleep(3)
while True:
    frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    res = detector.detect(gray)


    for r in res:
        print(r.tag_family, r.tag_id)
        corners = r.corners
        corners = np.ascontiguousarray(np.array(corners, dtype=np.float32).reshape((4,2,1)))
#        print(world_points[r.tag_id], corners, cameraMatrix, distCoeffs)
        retval, rvec, tvec = cv2.solvePnP(world_points, corners, cameraMatrix, np.zeros((4,1)))
        print(retval,rvec,tvec)
        for c in corners:
            c = tuple([int(x) for x in c])
            gray = cv2.circle(gray, c, 5, (255,0,0), 1)

    
    cv2.imshow('img', gray)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
