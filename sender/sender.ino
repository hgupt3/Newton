// sensor libraries
#include <LSM6DS3.h>
#include <Wire.h>

// network libraries
#include <SPI.h>
#include <WiFiNINA.h>
#include <WiFiUdp.h>
#include "arduino_secrets.h" // SSID and PASS

// initialize sensor variables
LSM6DS3 myIMU(I2C_MODE, 0x6A); 
float aX, aY, aZ, gX, gY, gZ, time, start_time = 0;

// initialize network variables
int status = WL_IDLE_STATUS;
char ssid[] = SECRET_SSID, pass[] = SECRET_PASS;
unsigned int localPort = 2390;
WiFiUDP Udp;
IPAddress recieverIP;
unsigned int recieverPort;
char packetBuffer[256]; // only first element will contain relevant data

void setup() {
  Serial.begin(115200);
  while (!Serial); // wait serial connection
  if (myIMU.begin() != 0) Serial.println("Sensor error"); //.begin() to configure the IMU

  // attempt to establish network
  Serial.println("Attempting to connect to WiFi");
  while (status != WL_CONNECTED) status = WiFi.begin(ssid, pass); // establish connection

  // begin listening on port
  Serial.println("Connected to WiFi");
  Udp.begin(localPort);
  
  // attempt to establish connection to reciever
  Serial.println("Attempting to connect to reciever");
  bool recieved = false;
  while (!recieved){ // until initialization packet from reciever is found
    if (check_UDP() && packetBuffer[0] == 'I'){ 
      recieved = true;
      Serial.println("Connected to reciever");
      recieverIP = Udp.remoteIP();  // remember for communication
      recieverPort = Udp.remotePort();
    }
  }
}

void loop() {
  if (check_serial() == 'R') start_time = micros()/ 1e6; // check for reset time signal
  send_data(); // send data to serial
  delay(100); // every 100ms
}

// function to check for and recieve signal
char check_serial() {
  if (Serial.available() > 0) return Serial.read();
}

// function to check for and read UDP packet
bool check_UDP() {
  bool recieved = false;
  if (Udp.parsePacket()){
    recieved = true;
    int len = Udp.read(packetBuffer, 255);
    if (len > 0) packetBuffer[len] = 0; // read packet to buffer
  }
  return recieved;
}

// function to send data to serial 
void send_data() {
  time = (micros() / 1e6) - start_time; // time relative to reset signal time

  // read data from sensor
  aX = myIMU.readFloatAccelX();
  aY = myIMU.readFloatAccelY();
  aZ = myIMU.readFloatAccelZ();
  gX = myIMU.readFloatGyroX();
  gY = myIMU.readFloatGyroY();
  gZ = myIMU.readFloatGyroZ();

  // broadcast to serial
  Serial.print(time);
  Serial.print(",");
  Serial.print(aX);
  Serial.print(",");
  Serial.print(aY);
  Serial.print(",");
  Serial.print(aZ);
  Serial.print(",");
  Serial.print(gX);
  Serial.print(",");
  Serial.print(gY);
  Serial.print(",");
  Serial.println(gZ);
}
