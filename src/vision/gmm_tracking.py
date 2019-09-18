import numpy as np
import time
import cv2
from sklearn import mixture
from imutils.video import FPS
import sys
np.set_printoptions(threshold=sys.maxsize)
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

def crop_center(img,cropx,cropy):
    y,x = img.shape
    startx = x//2-(cropx//2)
    starty = y//2-(cropy//2)    
    return img[starty:starty+cropy,startx:startx+cropx, :]

# Loading model
model = cv2.dnn.readNetFromTensorflow('../../data/models/frozen_inference_graph.pb',
                                      '../../data/models/ssd_mobilenet_v2_coco_2018_03_29.pbtxt')

cap = cv2.VideoCapture(0)

fps = FPS()
fps.start()
gmm = mixture.GaussianMixture(n_components=2, max_iter = 1000)
(H, W) = (None,None)
color = (0, 255, 0)
fit = False
innerSize = 100
sample = np.zeros([innerSize, innerSize])
cX, cY = 0,0
notFound = True
start = time.time()
frame_num = 0
while True:
    ret, frame = cap.read()
    frame_num += 1
    if W is None or H is None:
        (H,W) = frame.shape[0:2]
    if notFound:
        print('Tracking with DNN')
        model.setInput(cv2.dnn.blobFromImage(frame, size=(300,300), swapRB=True))
        output = model.forward()

        for detection in output[0,0,:,:]:
            confidence = detection[2]
            if confidence > 0.5:
                class_id = detection[1]
                class_name = id_class_name(class_id, classNames)

                if class_name == "person":
                    box = detection[3:7] * np.array([W, H, W, H])
                    startX, startY, endX, endY = box.astype('int')
                    cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)
                    cv2.putText(frame, str(), (10,10), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,0,255))
                    sample = frame[startY:endY, startX:endX, :]
        
                    if fit:
                        test = np.reshape(frame, [frame.shape[0]*frame.shape[1],3])
                        preds = gmm.predict(test)
                        pred_img = np.reshape(preds*255, [frame.shape[0],frame.shape[1],1])
                        notFound = False
                        cv2.imshow('pred',pred_img.astype('float32'))
                        

            if sample.shape[0] > 0 and sample.shape[1] > 0:
                cv2.imshow('sample', sample)
                    
    else:
        print('Tracking with only gmm')
        test = np.reshape(frame, [frame.shape[0]*frame.shape[1], 3])
        preds = gmm.predict(test)
        pred_img = np.reshape(preds*255, [frame.shape[0], frame.shape[1], 1])
        cv2.imshow('pred', pred_img.astype('uint8'))
        contours, _ = cv2.findContours(pred_img, cv2.RETR_FLOODFILL, cv2.CHAIN_APPROX_SIMPLE)
        for c in contours:
            rect = cv2.boundingRect(c)
            x,y,w,h = rect
            cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2)
    framesps = frame_num / (time.time() - start)

    cv2.putText(frame, str(framesps), (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,255,0), lineType=cv2.LINE_AA)
    cv2.imshow('image', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    if cv2.waitKey(35) & 0xFF == ord('c'):
        train_frames = 3
        train = np.zeros((train_frames, frame.shape[0], frame.shape[1], 3))
        for i in range(train_frames):
            r,f = cap.read()
            train[i, :, :,:] = f
        train = np.reshape(train, [frame.shape[0]*frame.shape[1]*train_frames ,3])
        gmm.fit(train)
        print('gmm trained')
        fit = True

    fps.update()

fps.stop()
print("FPS: {}".format(fps.fps()))
cap.release()
cv2.destroyAllWindows()


