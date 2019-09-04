from imutils.object_detection import non_max_suppression
from imutils import paths
import numpy as np
import imutils
import cv2
import argparse


cap = cv2.VideoCapture(0)

hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
face_cascade = cv2.CascadeClassifier('../../data/haarcascades/haarcascade_frontalface_default.xml')
upper_cascade = cv2.CascadeClassifier('../../data/haarcascades/haarcascade_upperbody.xml')
lower_cascade = cv2.CascadeClassifier('../../data/haarcascades/haarcascade_lowerbody.xml')

profile_cascade = cv2.CascadeClassifier('../../data/haarcascades/haarcascade_profileface.xml')
print(face_cascade)
while(True):
    ret, image = cap.read()

    image = cv2.resize(image, (640, 480))

    orig = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    uppers = upper_cascade.detectMultiScale(gray, 1.3, 5)
    lowers = lower_cascade.detectMultiScale(gray, 1.3, 5)
    profiles = profile_cascade.detectMultiScale(gray, 1.3, 5)

    for (x,y,w,h) in faces:
        cv2.rectangle(orig, (x,y), (x+w, y+h), (0, 0, 255), 2)

    for (x,y,w,h) in profiles:
        cv2.rectangle(orig, (x,y), (x+w, y+h), (0, 0, 255), 2)

    for (x,y,w,h) in uppers:
        cv2.rectangle(orig, (x,y), (x+w, y+h), (0, 255, 0), 2)

    for (x,y,w,h) in lowers:
        cv2.rectangle(orig, (x,y), (x+w, y+h), (255, 0, 0), 2)

    cv2.imshow("Before NMS", orig)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

