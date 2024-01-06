# this file recieves and decodes packets from the arduino. 
# this data is saved to 'data.csv' with timestamps

import socket
import csv
import numpy as np
import time
import os
import sys
import torch
from lstm_model import real_time_hand_lstm, ss_output, ss_input
from torch.autograd import Variable
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt

class reciever():
    def __init__(self, time_):
        # network variables and intialization
        self.senderIP = "192.168.1.10" # change to that of arduino
        self.senderPort = 2390
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # socket creation
        self.sock.settimeout(3) # after 3 seconds timeout
        self.data = []
        
        self.time = time_ + time.time()
    
    # function for processing and plotting real-time data 
    def run_real_time(self):
        self.model = real_time_hand_lstm()
        self.model.load_state_dict(torch.load("newton_model/weights.pth"))
        self.model.eval()

        self.fig = plt.figure()
        self.fig.canvas.manager.set_window_title('Newton')
        self.ax = self.fig.add_subplot(111, projection='3d') # create 3D figure
        self.ani = FuncAnimation(self.fig, self.create_plot_real_time, interval=1,
                                 cache_frame_data=False)
        
        self.sock.sendto(b'R', (self.senderIP, self.senderPort))
        plt.show()

    # function for running and gathering datasets (data collection)
    def run(self):
        # send time info to arduino
        self.sock.sendto(bytes(f'{time.time()}', 'utf-8'), (self.senderIP, self.senderPort))
         
        while self.time > time.time():
            self.read_data()
    
    def create_plot_real_time(self, n):
        try: recieved, addr = self.sock.recvfrom(1024) # buffer size is 1024 bytes
        except: plt.close()
        line = recieved.decode('utf-8').strip()
        values = line.split(',')
        for idx, elem in enumerate(values): values[idx] = float(elem)
            
        values = ss_input.transform([values[1:]])
        print(values)
        input_tensor = Variable(torch.Tensor(np.array([values])))

        output = self.model(input_tensor)
        output = output.data.numpy()
        output = ss_output.inverse_transform(output[0])[0]
        
        landmarks = []
        for idx in range(21):
            landmarks.append([output[idx*3], output[idx*3+1], output[idx*3+2]])
            
        # clear axes and set new ones
        self.ax.clear()
        self.ax.set_box_aspect((1, 1, 0.6), zoom = 1.6) # aspect ratio of graph
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("y")
        self.ax.set_zlabel("z")
        self.ax.set_xlim3d(-10, 10)
        self.ax.set_ylim3d(-10, 10)
        self.ax.set_zlim3d(-10, 10)
        self.ax.set_zticklabels([])
        self.ax.view_init(elev=-90, azim=270)

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

    # function for processing data from arduino
    def read_data(self): 
        try: recieved, addr = self.sock.recvfrom(1024) # buffer size is 1024 bytes
        except: self.close()
        line = recieved.decode('utf-8').strip()
        values = line.split(',')
        for idx in range(len(values)):
            try: self.data[idx].append(float(values[idx]))
            except: self.data.append([float(values[idx])])
    
    # function to save data to csv
    def save_data(self):
        # check for file name
        idx = 1
        while os.path.exists(f'data/reciever{idx}.csv'): idx += 1
        
        self.data = np.array(self.data)
        with open(f'data/reciever{idx}.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['T',
                             'Ax1','Ay1','Az1','Gx1','Gy1','Gz1',
                             'Ax2','Ay2','Az2','Gx2','Gy2','Gz2',
                             'Ax3','Ay3','Az3','Gx3','Gy3','Gz3',
                             'Ax4','Ay4','Az4','Gx4','Gy4','Gz4',
                             'Ax5','Ay5','Az5','Gx5','Gy5','Gz5'])
            for idx in range(self.data.shape[1]):
                writer.writerow(self.data[:,idx])
                
    def close(self):
        self.sock.close()
        self.save_data()
         
# run class   
try: rec = reciever(int(sys.argv[1]))
except: rec = reciever(20)
rec.run_real_time()
