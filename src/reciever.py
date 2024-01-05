# this file recieves and decodes packets from the arduino. 
# this data is saved to 'data.csv' with timestamps

import socket
import csv
import numpy as np
import time
import os
import sys

class reciever():
    def __init__(self, time_):
        # network variables and intialization
        self.senderIP = "192.168.1.10" # change to that of arduino
        self.senderPort = 2390
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # socket creation
        self.sock.settimeout(3) # after 3 seconds timeout
        self.data = []
        
        self.time = time_ + time.time()
        
    def run(self):
        # send time info to arduino
        self.sock.sendto(bytes(f'{time.time()}', 'utf-8'), (self.senderIP, self.senderPort))
         
        while self.time > time.time():
            self.read_data()
    
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
except: rec = reciever(5)
rec.run()
rec.close()
