import numpy as np
import cv2
from imutils.video import FPS, WebcamVideoStream
import sys
sys.path.append('..')

from vision import Tracker

fps = FPS().start()
cap = WebcamVideoStream(src=0).start()
initBB = None

tracker = Tracker.Tracker(0.8)

firstFrame = cap.read()
initBB = tracker.initialize(firstFrame)

while True:
    frame = cap.read()

    box = tracker.track(frame)
    (x,y,w,h) = box
    if box:
        cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0),2)

    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    fps.update()


fps.stop()
cv2.destroyAllWindows()
print(fps.fps())

