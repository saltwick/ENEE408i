import cv2
import numpy as np
import Tracker
import imutils
from imutils.video import FPS, WebcamVideoStream

tracker = cv2.TrackerMOSSE_create()
person_id = 1
model = cv2.dnn.readNetFromTensorflow('../../data/models/frozen_inference_graph.pb',
                                      '../../data/models/ssd_mobilenet_v2_coco_2018_03_29.pbtxt')

cap = WebcamVideoStream(src=0).start()
fps = FPS().start()
initBB = None
while True:
    frame = cap.read()


    frame = imutils.resize(frame, width=500)
    (H,W) = frame.shape[:2]

    if initBB is not None:
        (success, box) = tracker.update(frame)

        if success:
            (x,y,w,h) = [int(v) for v in box]
            cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0),2)
       
#        cv2.rectangle(frame, (initBB[0], initBB[1]), (initBB[2], initBB[3]), (0,255,0), 2) 


    cv2.imshow('frame', frame)
    fps.update()
    key = cv2.waitKey(1) & 0xFF
    if key == ord('s'):
        initBB = cv2.selectROI("Frame", frame, fromCenter=False, showCrosshair=True)
        print(type(initBB))
        tracker.init(frame, initBB)
        fps = FPS().start()

    if key == ord('d'):
        init_frame = cap.read()
        model.setInput(cv2.dnn.blobFromImage(init_frame, size=(300,300),swapRB=True))
        output = model.forward()
        for detection in output[0,0,:,:]:
            confidence = detection[2]
            if confidence > 0.5:
                class_id = detection[1]
                if class_id == person_id:
                    box_x = detection[3] * W
                    box_y = detection[4] * H
                    box_width = detection[5] * W
                    box_height = detection[6] * H
                    box = detection[3:7] * np.array([W,H,W,H])
                    initBB = box.astype('int')

        if initBB is not None:
            print("initializing tracker at {}".format(tuple(initBB)))
            tracker.init(init_frame, tuple(initBB))
            fps = FPS().start()
        else:
            print("Failed to detect")

    if key == ord('q'):
        break

fps.stop()
cv2.destroyAllWindows()
print(fps.fps())






