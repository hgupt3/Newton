import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import csv

# arduino connection intialization
arduino = serial.Serial(port='/dev/cu.usbmodem1101', baudrate=115200) 

# commented code finds arduino port address

# import serial.tools.list_ports
# ports = serial.tools.list_ports.comports()
# for port in ports: print(port)

# lists to store data
T,Ax,Ay,Az,Gx,Gy,Gz = [],[],[],[],[],[],[]

# function for processing data from arduino
def read_data(): 
    line = arduino.readline().decode('utf-8').strip()
    values = line.split(',')
    T.append(float(values[0]))
    Ax.append(float(values[1]))
    Ay.append(float(values[2]))
    Az.append(float(values[3]))
    Gx.append(float(values[4]))
    Gy.append(float(values[5]))
    Gz.append(float(values[6]))
    # print(f'Time: {T[-1]}, Ax: {Ax[-1]}, Ay: {Ay[-1]}, Az: {Az[-1]}, Gx: {Gx[-1]}, Gy: {Gy[-1]}, Gz: {Gz[-1]}')
    
# function to update plot
def update_plot(frame):
    read_data()
    plt.cla()
    plt.plot(T, Ax, label='Ax')
    plt.plot(T, Ay, label='Ay')
    plt.plot(T, Az, label='Az')
    plt.plot(T, Gx, label='Gx')
    plt.plot(T, Gy, label='Gy')
    plt.plot(T, Gz, label='Gz')
    plt.xlabel('Time')
    plt.ylabel('Sensor Values')
    plt.legend()
    
# function to save data to csv
def save_data(event):
    with open('data.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Time','Ax','Ay','Az','Gx','Gy','Gz'])
        for t,ax,ay,az,gx,gy,gz in zip(T,Ax,Ay,Az,Gx,Gy,Gz):
            writer.writerow([t,ax,ay,az,gx,gy,gz])

# send reset char to arduino
arduino.write(b'R') 

# configure plot
fig, ax = plt.subplots()
fig.canvas.mpl_connect('close_event', save_data) # save data once plot is closed
ani = FuncAnimation(fig, update_plot, interval=10)
plt.show()