# Newton Hand

Below is a demo of the real-time spatial model created using the Newton Hand:


![Newton Demo](https://github.com/hgupt3/Newton/assets/112455192/fdeeb6dc-2994-427f-a9a1-2890a4782db0)


# Data Flow

This diagram describes the data flow every 100ms. 

Sensor data is iteratively collected through the I2C channel using a multiplexer. The data is wrapped into a UDP packet sent to the server to be processed.

After the data is recieved, unpacked, and processed, the server passes the data through a recurrent neural network with a 30 node input layer (6 inputs per sensor), 2 - 128 node LSTM layers, a 84 node linear layer, and a 63 node output layer (xyz coordinates for 21 landmarks). In the LSTM layer, after each iteration, the hidden states and cell states are stored (initial are 0s) and used in the next 100ms cycle. 

The output landmarks can be used in different applications as demonstrated in https://youtu.be/aYTmjKz988A. 


![JPEG image-4393-92E7-0C-0](https://github.com/hgupt3/Newton/assets/112455192/ace51bf3-89e6-4b83-b25e-3215baa14e95)


# Hardware

The hardware used in the Newton Hand prototype includes:

- Arduino MKR WiFi 1010 
- Arduino MKR Connector Carrier
- 5x Grove 6-Axis Accelerometer & Gyroscope
- Grove 8 Channel I2C Multiplexer


![IMG_5843](https://github.com/hgupt3/Newton/assets/112455192/5d5d06a6-7e06-4a08-b2e8-408ade828063)
