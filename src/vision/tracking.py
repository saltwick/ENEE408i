import cv2
import time
from imutils.video import FPS
from CentroidTracker import CentroidTracker
import numpy as np
# Pretrained classes in the model
classNames = {0: 'background',
              1: 'person', 2: 'bicycle', 3: 'car', 4: 'motorcycle', 5: 'airplane', 6: 'bus',
              7: 'train', 8: 'truck', 9: 'boat', 10: 'traffic light', 11: 'fire hydrant',
              13: 'stop sign', 14: 'parking meter', 15: 'bench', 16: 'bird', 17: 'cat',
              18: 'dog', 19: 'horse', 20: 'sheep', 21: 'cow', 22: 'elephant', 23: 'bear',
              24: 'zebra', 25: 'giraffe', 27: 'backpack', 28: 'umbrella', 31: 'handbag',
              32: 'tie', 33: 'suitcase', 34: 'frisbee', 35: 'skis', 36: 'snowboard',
              37: 'sports ball', 38: 'kite', 39: 'baseball bat', 40: 'baseball glove',
              41: 'skateboard', 42: 'surfboard', 43: 'tennis racket', 44: 'bottle',
              46: 'wine glass', 47: 'cup', 48: 'fork', 49: 'knife', 50: 'spoon',
              51: 'bowl', 52: 'banana', 53: 'apple', 54: 'sandwich', 55: 'orange',
              56: 'broccoli', 57: 'carrot', 58: 'hot dog', 59: 'pizza', 60: 'donut',
              61: 'cake', 62: 'chair', 63: 'couch', 64: 'potted plant', 65: 'bed',
              67: 'dining table', 70: 'toilet', 72: 'tv', 73: 'laptop', 74: 'mouse',
              75: 'remote', 76: 'keyboard', 77: 'cell phone', 78: 'microwave', 79: 'oven',
              80: 'toaster', 81: 'sink', 82: 'refrigerator', 84: 'book', 85: 'clock',
              86: 'vase', 87: 'scissors', 88: 'teddy bear', 89: 'hair drier', 90: 'toothbrush'}


def id_class_name(class_id, classes):
    for key, value in classes.items():
        if class_id == key:
            return value

ct = CentroidTracker()
(H,W) = (None, None)
# Loading model
model = cv2.dnn.readNetFromTensorflow('../../data/models/frozen_inference_graph.pb',
                                      '../../data/models/ssd_mobilenet_v2_coco_2018_03_29.pbtxt')
image = cv2.imread("../../data/images/people.jpeg")

cap = cv2.VideoCapture(0)
if cap.isOpened():
    print('Initializing Camera')
    for i in range(10):
        _,_ = cap.read()
        time.sleep(0.2)
print('Camera Initialized')

fps = FPS().start()
while(True):
    ret, image = cap.read()
    image_height, image_width, _ = image.shape
    if W is None or H is None:
        (H,W) = image.shape[:2]

    model.setInput(cv2.dnn.blobFromImage(image, size=(300, 300), swapRB=True))
    output = model.forward()
    rects = []
    for detection in output[0, 0, :, :]:
        confidence = detection[2]
        if confidence > .7:
            class_id = detection[1]
            class_name=id_class_name(class_id,classNames)

            if class_name == "person":
                box_x = detection[3] * image_width
                box_y = detection[4] * image_height
                box_width = detection[5] * image_width
                box_height = detection[6] * image_height
                box = detection[3:7] * np.array([W, H, W, H])
                startX, startY, endX, endY = box.astype('int')
                rects.append(box)
                cv2.rectangle(image, (startX, startY), (endX, endY), (0,255,0), 2)

                objects = ct.update(rects=rects)

                for (objectID, centroid) in objects.items():
                    text = "ID {}".format(objectID)
                    cv2.putText(image, text, (centroid[0] - 10, centroid[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255,0), 2)
                    cv2.circle(image, (centroid[0], centroid[1]), 4, (255,0,0), -1)

    cv2.imshow('image', image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    fps.update()

fps.stop()
print("Approximate FPS was {}".format(fps.fps()))
cap.release()
cv2.destroyAllWindows()
