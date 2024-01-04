# this file takes a video feed of a hand, landmarks it and
# gives finger locations relative to the center of the hand

import cv2
import time
import mediapipe as mp
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np
import csv
import os
import sys

# hand landmarker class to output landmarks
# more details at https://developers.google.com/mediapipe/solutions/vision/hand_landmarker/python#live-stream
class hand_landmarker():
    def __init__(self):
        self.result = mp.tasks.vision.HandLandmarkerResult
        self.landmarker = mp.tasks.vision.HandLandmarker
        self.create_landmarker()
    
    # initialize landmarker using custom options
    def create_landmarker(self):
        # callback function
        def update_result(result: mp.tasks.vision.HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
            self.result = result
          
        options = mp.tasks.vision.HandLandmarkerOptions( 
         base_options = mp.tasks.BaseOptions(model_asset_path="./mp_model/hand_landmarker.task"), # path to model
         running_mode = mp.tasks.vision.RunningMode.LIVE_STREAM, # running on a live stream
         result_callback=update_result)
        self.landmarker = self.landmarker.create_from_options(options)
    
    # detect landmarks
    def detect_async(self, frame):
      mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame) # convert np frame to mediapipe image
      self.landmarker.detect_async(image = mp_image, timestamp_ms = int(time.time() * 1000)) 
      
    def close(self):
      self.landmarker.close()
    
class camera():
    def __init__(self, time_):
        self.landmarker = hand_landmarker() # create hand landmarker instance
        self.frame, self.ret = None, None
        self.data = []
        
        self.time = time_ + time.time()
        
    def run(self):
        self.feed = cv2.VideoCapture(0) # try 0 or 1 if you get an error
        self.feed.isOpened()
        
        while self.time > time.time():
            self.update()
        
    # update plot function which reads frame and displays landmarks
    def update(self):        
        self.ret, unprocessed_frame = self.feed.read() # read and display frame
        self.landmarker.detect_async(unprocessed_frame) # detect landmarks
        landmarks = self.landmarker.result
        
        self.frame = draw_landmarks(unprocessed_frame, landmarks) 
        
        cv2.imshow('Camera', self.frame)
        cv2.namedWindow("Camera", cv2.WINDOW_NORMAL) 
        cv2.resizeWindow("Camera", 900, 500)
        if cv2.waitKey(1) in {ord("q"), ord("Q")}: self.close('close_event')
        
        landmarks = process_data(landmarks) * 100
        
        # if landmarks found then append
        if len(landmarks): self.data.append(np.append([time.time()], landmarks))
        
    def save_data(self):
        # check for file name
        idx = 1
        while os.path.exists(f'data/camera{idx}.csv'): idx += 1
        
        # write data to file
        with open(f'data/camera{idx}.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['T',
                             '0x','0y','0z','1x','1y','1z','2x','2y','2z','3x','3y','3z','4x','4y','4z',
                             '5x','5y','5z','6x','6y','6z','7x','7y','7z','8x','8y','8z','9x','9y','9z',
                             '10x','10y','10z','11x','11y','11z','12x','12y','12z','13x','13y','13z',
                             '14x','14y','14z','15x','15y','15z','16x','16y','16z','17x','17y','17z',
                             '18x','18y','18z','19x','19y','19z','20x','20y','20z'])
            for idx in range(len(self.data)):
                writer.writerow(np.around(self.data[idx],2))
            
    # closes all instances
    def close(self):
        self.feed.release()
        self.save_data()
      
# adapted from https://github.com/googlesamples/mediapipe/blob/main/examples/hand_landmarker/python/hand_landmarker.ipynb 
def draw_landmarks(image, landmarks):
    annotated_image = np.copy(image)
    try:
        landmarks = landmarks.hand_landmarks[0] # extract camera landmarks of first hand
        hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        hand_landmarks_proto.landmark.extend([
        landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in landmarks])
        solutions.drawing_utils.draw_landmarks(
        annotated_image,
        hand_landmarks_proto,
        solutions.hands.HAND_CONNECTIONS,
        solutions.drawing_styles.get_default_hand_landmarks_style(),
        solutions.drawing_styles.get_default_hand_connections_style())
    finally: return annotated_image

def process_data(unprocessed_landmarks):
    landmarks = []
    try: 
        unprocessed_landmarks = unprocessed_landmarks.hand_world_landmarks[0] # extract world landmarks of first hand
        landmarks = np.zeros((21,3))
        for idx in range(len(unprocessed_landmarks)): # put x y z in an easily mutable array
            landmarks[idx,:] = unprocessed_landmarks[idx].x, unprocessed_landmarks[idx].y, unprocessed_landmarks[idx].z
    finally: return landmarks

# show camera    
cam = camera(int(sys.argv[1]))
cam.run()
cam.close()
