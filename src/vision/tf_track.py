import cv2
import numpy
from imutils.video import FPS, WebcamVideoStream
import tensorflow as tf


cap = WebcamVideoStream(src=0).start()

fps = FPS().start()


while True:
    frame = cap.read()

    cv2.imshow('frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    fps.update()

fps.stop()
cv2.destroyAllWindows()
print(fps.fps())
