// this file sets up the arduino's network and begins transmission 
// to 'reciever.py' once an initialization/reset byte is recieved

#include <string.h>
using namespace std;

// component libraries
#include <LSM6DS3.h>
#include "TCA9548A.h"
#include <Wire.h>

// network libraries
#include <SPI.h>
#include <WiFiNINA.h>
#include <utility/wifi_drv.h>
#include <WiFiUdp.h>
#include "network_info.h" // SSID and PASS


// ARDUINO DEBUGGING INDICATORS: 
// RED LIGHT           -> Not connected to WiFi
// BLINKING RED LIGHT  -> Sensor Error
// BLUE LIGHT          -> Awaiting signal from reciever
// GREEN LIGHT         -> Transmitting packets to reciever

// initialize component variables
TCA9548A<TwoWire> TCA;
LSM6DS3 myIMU(I2C_MODE, 0x6A); 
float aX, aY, aZ, gX, gY, gZ, time, start_time = 0;
int channel_ = -1; // specifices which channel is currently open on MUX/TCA

// TCA CHANNEL 0 AND 1 MANIPULATION CAUSES NETWORK MODULE TO DISCONNECT RANDOMLY DURING SKETCH

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
  // uncomment below for reliable serial connection
  // while(!Serial); // wait for serial connection

  TCA.begin(Wire); // begin communication to I2C multplexer
  
  for (int idx = 2; idx < 7; idx++){ // iterate through all channels
    channel(idx);
    if (myIMU.begin() != 0) { //.begin() to configure the IMU
      Serial.println("Sensor error");
      while (myIMU.begin() != 0) { // blinking red light indicating sensor error
        blank();
        delay(1000);
        red();
        delay(1000);
      }
    } 
  }

  network_intilization(); // configure the network

  green(); // green color i.e. data communication

  Serial.println("Beginning data communication");
  Serial.println("-------------------------------------------");
  start_time = (micros() / 1e6); // reset time
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    red();
    Serial.println("Communication with WiFi failed");
    while (true); // don't continue
  }

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
  String msg = "";

  // iterate through all channels
  for (int idx = 2; idx < 7; idx++) {
    channel(idx);
    // read data from sensor
    time = (micros() / 1e6) - start_time; // time relative to reset signal time
    aX = myIMU.readFloatAccelX();
    aY = myIMU.readFloatAccelY();
    aZ = myIMU.readFloatAccelZ();
    gX = myIMU.readFloatGyroX();
    gY = myIMU.readFloatGyroY();
    gZ = myIMU.readFloatGyroZ();
    if (msg=="") {msg = String(time)+","+String(aX)+","+String(aY)+","+String(aZ)+","+String(gX)+","+String(gY)+","+String(gZ);}
    else {msg = msg+","+String(time)+","+String(aX)+","+String(aY)+","+String(aZ)+","+String(gX)+","+String(gY)+","+String(gZ);}
  }

  // send packet
  Udp.beginPacket(recieverIP, recieverPort);
  Udp.print(msg);
  Udp.endPacket();

  Serial.print("Sent packet at ");
  Serial.println(time);
}

// function to change I2C bus channel
void channel(unsigned int num){
  // close current channel
  if (channel_ == 0) TCA.closeChannel(TCA_CHANNEL_0);
  if (channel_ == 1) TCA.closeChannel(TCA_CHANNEL_1);
  if (channel_ == 2) TCA.closeChannel(TCA_CHANNEL_2);
  if (channel_ == 3) TCA.closeChannel(TCA_CHANNEL_3);
  if (channel_ == 4) TCA.closeChannel(TCA_CHANNEL_4);
  if (channel_ == 5) TCA.closeChannel(TCA_CHANNEL_5);
  if (channel_ == 6) TCA.closeChannel(TCA_CHANNEL_6);
  if (channel_ == 7) TCA.closeChannel(TCA_CHANNEL_7);
  
  // open channel specified
  if (num == 0) TCA.openChannel(TCA_CHANNEL_0);
  if (num == 1) TCA.openChannel(TCA_CHANNEL_1);
  if (num == 2) TCA.openChannel(TCA_CHANNEL_2);
  if (num == 3) TCA.openChannel(TCA_CHANNEL_3);
  if (num == 4) TCA.openChannel(TCA_CHANNEL_4);
  if (num == 5) TCA.openChannel(TCA_CHANNEL_5);
  if (num == 6) TCA.openChannel(TCA_CHANNEL_6);
  if (num == 7) TCA.openChannel(TCA_CHANNEL_7);

  channel_ = num; // remember opened channel
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
