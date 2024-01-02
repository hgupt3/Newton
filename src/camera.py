# this file takes a video feed of a hand, landmarks it and
# gives finger locations relative to the center of the hand

import cv2
import time
import mediapipe as mp
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import csv

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
    
class hand_plot():
    def __init__(self):
        self.landmarker = hand_landmarker() # create hand landmarker instance
        self.feed = cv2.VideoCapture(0) # try 0 or 1 if you get an error
        self.frame, self.ret = None, None
        self.data = []
        
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d') # create 3D figure 
        self.ani = FuncAnimation(self.fig, self.update_plot, interval=10, cache_frame_data=False)
        
        self.create_plot()
    
    # plot configuration
    def create_plot(self):
        self.feed.isOpened()
        self.fig.canvas.manager.set_window_title('Hand Landmark Plot')
        self.fig.canvas.mpl_connect('close_event', self.close) # call close if plot is closed
        self.start_time = time.time()
        plt.show()
        
    # update plot function which reads frame and displays landmarks
    def update_plot(self, num):         
        # clear axes and set new ones
        plt.cla() 
        self.ax.set_box_aspect((1, 1, 0.6), zoom = 1.6) # aspect ratio of graph
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("y")
        self.ax.set_zlabel("z")
        self.ax.set_xlim3d(-0.2, 0.2)
        self.ax.set_ylim3d(-0.2, 0.2)
        self.ax.set_zlim3d(-0.1, 0.1)
        self.ax.set_zticklabels([])
        self.ax.view_init(elev=-90, azim=270)
        
        self.ret, frame = self.feed.read() # read and display frame
        self.landmarker.detect_async(frame) # detect landmarks
        landmarks = self.landmarker.result
        
        self.frame = draw_landmarks(frame, landmarks) 
        cv2.imshow('Camera',self.frame) 
        landmarks = process_data(landmarks)
        if not len(landmarks): return # if no hands/landmarks found return
        self.data.append(np.append([time.time()-self.start_time], landmarks))
        
        # landmarks in order of their corresponding bodies
        palm_idx = {0, 17, 13, 9, 5, 0, 1}
        thumb_idx = {2, 3, 4}
        index_idx = {6, 7, 8}
        middle_idx = {10, 11, 12}
        ring_idx = {14, 15, 16}
        pinky_idx = {18, 19, 20}
        
        for idx in range(len(landmarks)): # print all landmarks 
            if idx in palm_idx: self.ax.scatter(landmarks[idx][0], landmarks[idx][1], landmarks[idx][2], color='red', edgecolors='white')
            if idx in thumb_idx: self.ax.scatter(landmarks[idx][0], landmarks[idx][1], landmarks[idx][2], color='bisque', edgecolors='white')
            if idx in index_idx: self.ax.scatter(landmarks[idx][0], landmarks[idx][1], landmarks[idx][2], color='purple', edgecolors='white')
            if idx in middle_idx: self.ax.scatter(landmarks[idx][0], landmarks[idx][1], landmarks[idx][2], color='gold', edgecolors='white')
            if idx in ring_idx: self.ax.scatter(landmarks[idx][0], landmarks[idx][1], landmarks[idx][2], color='chartreuse', edgecolors='white')
            if idx in pinky_idx: self.ax.scatter(landmarks[idx][0], landmarks[idx][1], landmarks[idx][2], color='royalblue', edgecolors='white')
        
        # create line connections between relevant landmarks
        palm = np.array([landmarks[0], landmarks[17], landmarks[13], landmarks[9], landmarks[5], landmarks[0], landmarks[1]])
        thumb = np.array([landmarks[1], landmarks[2], landmarks[3], landmarks[4]])
        index = np.array([landmarks[5], landmarks[6], landmarks[7], landmarks[8]])
        middle = np.array([landmarks[9], landmarks[10], landmarks[11], landmarks[12]])
        ring = np.array([landmarks[13], landmarks[14], landmarks[15], landmarks[16]])
        pinky = np.array([landmarks[17], landmarks[18], landmarks[19], landmarks[20]])
        
        # displayed with colors
        self.ax.plot(palm[:,0], palm[:,1], palm[:,2], color='grey')
        self.ax.plot(thumb[:,0], thumb[:,1], thumb[:,2], color='bisque')
        self.ax.plot(index[:,0], index[:,1], index[:,2], color='purple')
        self.ax.plot(middle[:,0], middle[:,1], middle[:,2], color='gold')
        self.ax.plot(ring[:,0], ring[:,1], ring[:,2], color='chartreuse')
        self.ax.plot(pinky[:,0], pinky[:,1], pinky[:,2], color='royalblue')
        
    def save_data(self):
        with open('data_camera.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['T',
                             '0x','0y','0z','1x','1y','1z','2x','2y','2z','3x','3y','3z','4x','4y','4z',
                             '5x','5y','5z','6x','6y','6z','7x','7y','7z','8x','8y','8z','9x','9y','9z',
                             '10x','10y','10z','11x','11y','11z','12x','12y','12z','13x','13y','13z',
                             '14x','14y','14z','15x','15y','15z','16x','16y','16z','17x','17y','17z',
                             '18x','18y','18z','19x','19y','19z','20x','20y','20z'])
            for idx in range(len(self.data)):
                writer.writerow(np.around(self.data[idx],4))
            
    # closes all instances
    def close(self, event):
        self.feed.release()
        plt.close()
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

# show hand landmark plot    
hand_plot()
