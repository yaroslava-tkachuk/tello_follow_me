"""Copyright 2022 Yaroslava Tkachuk. All rights reserved."""

"""[Work in progress]"""

import cv2
import numpy as np


video_capture = cv2.VideoCapture(0)

class_name = "person"
model_config_file_path = "yolov3.cfg"
model_weights_file_path = "yolov3.weights"

network = cv2.dnn.readNetFromDarknet(model_config_file_path, model_weights_file_path)
network.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
network.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)


while 1:
    img_retrieved, img = video_capture.read()
    if img_retrieved:
        # detect face
        cv2.dnn.blobFromImage()

        cv2.imshow("Camera Stream", img)
        cv2.waitKey(1)