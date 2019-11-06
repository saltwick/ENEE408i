import numpy as np
import cv2
import glob
import json

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((6*9,3), np.float32)
objp[:,:2] = np.mgrid[0:9,0:6].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

images = glob.glob('/home/nvidia/Pictures/Webcam/*.jpg')
cameraMatrix = np.zeros((3,3))
distCoeffs = np.zeros((1,4))
imgSize = None
cameraMatrices = []
distCoeffs = []
for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    imgSize = gray.shape[::-1]
    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, (9,6),None)
    print(fname)
    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)

        corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
        imgpoints.append(corners2)
        
        
        # Draw and display the corners
        img = cv2.drawChessboardCorners(img, (7,6), corners2,ret)
        ret, mtx, dist, rvecs,tvecs = cv2.calibrateCamera(objpoints, imgpoints, imgSize, None, None)
        cameraMatrices.append(mtx)
        distCoeffs.append(dist)
#        cv2.imshow('img',img)
#        cv2.waitKey(500)

print("Average Stats --------------------------------------------")
print("Average Camera Matrix")
print(sum(cameraMatrices)/len(cameraMatrices))
print("Average Distortion Coefficients")
print(sum(distCoeffs)/len(distCoeffs))

params = {}
params['cameraMatrix'] = (sum(cameraMatrices)/len(cameraMatrices)).tolist()
params['distCoeffs'] = (sum(distCoeffs)/len(distCoeffs)).tolist()

with open('cameraParams.json', 'w') as f:
    json.dump(params, f)

cv2.destroyAllWindows()
