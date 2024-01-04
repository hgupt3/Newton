import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# class which takes camera / prediction dataframe and plots it
class hand_plot():
    def __init__(self, df, interval_):
        self.data = df.to_numpy()

        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d') # create 3D figure
        self.ani = FuncAnimation(self.fig, self.update_plot, interval=interval_, cache_frame_data=False, frames=np.shape(self.data)[0])

    # plot configuration
    def create_plot(self):
        self.fig.canvas.manager.set_window_title('Hand Landmark Plot')
        plt.show()

    # update plot function which reads frame and displays landmarks
    def update_plot(self, num):
    
        landmarks = []
        self.data[num]
        for idx in range(21):
            landmarks.append([self.data[num][idx*3], self.data[num][idx*3+1], self.data[num][idx*3+2]])
            
        # clear axes and set new ones
        plt.cla()
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