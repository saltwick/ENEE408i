import cv2
import numpy as np

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

class Tracker():

    def __init__(self, confidence):
        print("Tracker Initialized")
        print(len(classNames))
        self.model = cv2.dnn.readNetFromTensorflow('../../data/models/frozen_inference_graph.pb',
                                      '../../data/models/ssd_mobilenet_v2_coco_2018_03_29.pbtxt')
        self.confidence = confidence
        self.cv_tracker = cv2.TrackerMOSSE_create()

    def id_class_name(self, class_id, classes):
        for key, value in classes.items():
            if class_id == key:
                return value

    def initialize(self, frame):
        (H,W) = frame.shape[:2]
        
        self.model.setInput(cv2.dnn.blobFromImage(frame, size=(300,300), swapRB=True))
        output = self.model.forward()
        to_track = ()
        img_height, img_width,_ = frame.shape
        for detection in output[0,0,:,:]:
            confid = detection[2]
            if confid > self.confidence:
                class_id = detection[1]
                class_name = self.id_class_name(class_id, classNames)

                if class_name == "person":
                    to_track = (detection[3] * img_width, detection[4] * img_height,
                            detection[5] * img_width, detection[6] * img_height)
                    self.cv_tracker.init(frame, to_track)
                    return to_track

    def track(self, frame, initBB):
        (success, box) = self.cv_tracker.update(frame)
        if success:
            (x,y,w,h) = [int(v) for v in box]

            return (x + int(w/4),y,int(w/2),h)


        
        
