#include <string.h>
using namespace std;

// sensor libraries
#include <LSM6DS3.h>
#include <Wire.h>

// network libraries
#include <SPI.h>
#include <WiFiNINA.h>
#include <utility/wifi_drv.h>
#include <WiFiUdp.h>
#include "network_info.h" // SSID and PASS

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
char packetBuffer[UDP_TX_PACKET_MAX_SIZE]; // only first element will contain relevant data

void setup() {
  WiFiDrv::pinMode(25, OUTPUT); //define green pin
  WiFiDrv::pinMode(26, OUTPUT); //define red pin
  WiFiDrv::pinMode(27, OUTPUT); //define blue pin

  red(); // red color i.e. no internet

  Serial.begin(115200);
  delay(1000); // wait for serial connection
  Serial.println(" ");
  Serial.println(" ");
  
  if (myIMU.begin() != 0) {
    Serial.println("Sensor error");
    while (myIMU.begin() != 0) { // blinking red light indicating sensor error
      blank();
      delay(1000);
      red();
      delay(1000);
    }
  } //.begin() to configure the IMU
  network_intilization(); // configure the network

  green(); // green color i.e. data communication

  Serial.println("Beginning data communication");
  Serial.println("-------------------------------------------");
  start_time = (micros() / 1e6); // reset time
}

void loop() {
  if (check_UDP() && packetBuffer[0] == 'R') {  // check for reset signal
    recieverIP = Udp.remoteIP();  // remember for communication
    recieverPort = Udp.remotePort();
    start_time = micros()/ 1e6;
  }
  send_data(); // send data through UDP
  delay(100); // every 100ms
}

// function to intilize network and print debugging information
void network_intilization() {
  // attempt to establish network
  Serial.println("-------------------------------------------");
  Serial.print("Attempting to connect to WiFi: ");
  // IPAddress localIP(10,14,1,244); // uncomment code to fix to certain IP
  // WiFi.config(localIP);
  while (status != WL_CONNECTED) status = WiFi.begin(ssid, pass); // establish connection

  blue(); // blue color i.e. awaiting intialization

  // begin listening on port
  Serial.println("Success");
  Udp.begin(localPort);

  // debugging info
  Serial.println("-------------------------------------------");
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  Serial.print("GATEWAY: ");
  Serial.println(WiFi.gatewayIP());

  Serial.print("LOCAL IP: ");
  Serial.println(WiFi.localIP());

  byte mac[6];   
  WiFi.macAddress(mac);
  Serial.print("MAC ADDRESS: ");
  Serial.print(mac[5],HEX);
  Serial.print(":");
  Serial.print(mac[4],HEX);
  Serial.print(":");
  Serial.print(mac[3],HEX);
  Serial.print(":");
  Serial.print(mac[2],HEX);
  Serial.print(":");
  Serial.print(mac[1],HEX);
  Serial.print(":");
  Serial.println(mac[0],HEX);
  Serial.println("-------------------------------------------");
  
  // attempt to establish connection to reciever
  Serial.print("Attempting to connect to reciever: ");
  bool recieved = false;
  while (!recieved){ // until initialization packet from reciever is found
    if (check_UDP() && packetBuffer[0] == 'R'){ 
      recieved = true;
      Serial.println("Success");
      recieverIP = Udp.remoteIP();  // remember for communication
      recieverPort = Udp.remotePort();
    }
  }
  Serial.println("-------------------------------------------");
  Serial.print("RECIEVER IP: ");
  Serial.println(recieverIP);
  Serial.print("RECIEVER PORT: ");
  Serial.println(recieverPort);
  Serial.println("-------------------------------------------");
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

// function to send data through UDP 
void send_data() {
  time = (micros() / 1e6) - start_time; // time relative to reset signal time

  // read data from sensor
  aX = myIMU.readFloatAccelX();
  aY = myIMU.readFloatAccelY();
  aZ = myIMU.readFloatAccelZ();
  gX = myIMU.readFloatGyroX();
  gY = myIMU.readFloatGyroY();
  gZ = myIMU.readFloatGyroZ();
  
  String msg = String(time)+","+String(aX)+","+String(aY)+","+String(aZ)+","+String(gX)+","+String(gY)+","+String(gZ);

  // send packet
  Udp.beginPacket(recieverIP, recieverPort);
  Udp.print(msg);
  Udp.endPacket();

  Serial.print("Sent packet at ");
  Serial.println(time);
}

// toggle pin color functions
void red() {
  WiFiDrv::analogWrite(25, 1);
  WiFiDrv::analogWrite(26, 0);
  WiFiDrv::analogWrite(27, 0);
}

void blue() {
  WiFiDrv::analogWrite(25, 0);
  WiFiDrv::analogWrite(26, 0);
  WiFiDrv::analogWrite(27, 1);
}

void green() {
  WiFiDrv::analogWrite(25, 0);
  WiFiDrv::analogWrite(26, 1);
  WiFiDrv::analogWrite(27, 0);
}

void blank() {
  WiFiDrv::analogWrite(25, 0);
  WiFiDrv::analogWrite(26, 0);
  WiFiDrv::analogWrite(27, 0);
}
