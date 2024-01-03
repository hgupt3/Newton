# this file recieves and decodes packets from the arduino. 
# this data is saved to 'data.csv' with timestamps

import socket
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import csv
import numpy as np
import time

class reciever():
    def __init__(self):
        # network variables and intialization
        self.senderIP = "192.168.1.10" # change to that of arduino
        self.senderPort = 2390
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # socket creation
        self.sock.settimeout(3) # after 3 seconds timeout
        self.start_time = 0
        
        # lists to store data
        self.data = []
        
        # create plot
        self.fig, self.ax = plt.subplots(1, 5) 
        self.ani = FuncAnimation(self.fig, self.update_plot, interval=100, cache_frame_data=False)
        self.begin_reciever()
        
    # function to start reciever functions
    def begin_reciever(self):
        # send reset char to arduino
        self.sock.sendto(b'R', (self.senderIP, self.senderPort))
        self.start_time = time.time()
        # configure plot
        self.fig.canvas.mpl_connect('close_event', self.close) # close function once plot closed
        self.fig.canvas.manager.set_window_title('Accelerometer Plot')
        plt.show()
    
    # function for processing data from arduino
    def read_data(self): 
        try: recieved, addr = self.sock.recvfrom(1024) # buffer size is 1024 bytes
        except: self.close('Packet timeout')
        line = recieved.decode('utf-8').strip()
        values = line.split(',')
        for idx in range(len(values)):
            try: self.data[idx].append(float(values[idx]))
            except: self.data.append([float(values[idx])])
    
    # function to update plot
    def update_plot(self, frame):
        self.read_data()
        for idx in range(len(self.data) // 7):
            self.ax[idx].cla()
            self.ax[idx].set_ylim(-2, 2)
            self.ax[idx].set_xticks([])
            self.ax[idx].set_yticks([])
            self.ax[idx].plot(self.data[7*idx][-20:], self.data[1+7*idx][-20:], label='Ax')
            self.ax[idx].plot(self.data[7*idx][-20:], self.data[2+7*idx][-20:], label='Ay')
            self.ax[idx].plot(self.data[7*idx][-20:], self.data[3+7*idx][-20:], label='Az')
    
    # function to save data to csv
    def save_data(self):
        self.data = np.array(self.data)
        with open('data/data_reciever.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['T1','Ax1','Ay1','Az1','Gx1','Gy1','Gz1',
                             'T2','Ax2','Ay2','Az2','Gx2','Gy2','Gz2',
                             'T3','Ax3','Ay3','Az3','Gx3','Gy3','Gz3',
                             'T4','Ax4','Ay4','Az4','Gx4','Gy4','Gz4',
                             'T5','Ax5','Ay5','Az5','Gx5','Gy5','Gz5'])
            for idx in range(self.data.shape[1]):
                writer.writerow(self.data[:,idx])
                
    def close(self, event):
        plt.close()
        self.sock.close()
        self.save_data()
         
# run class   
reciever()