#include <LSM6DS3.h>
#include <Wire.h>

// initialize IMU and variables
LSM6DS3 myIMU(I2C_MODE, 0x6A); 
float aX, aY, aZ, gX, gY, gZ, time, start_time = 0;
void setup() {
  Serial.begin(115200);
  while (!Serial);
  //.begin() to configure the IMU
  if (myIMU.begin() != 0) Serial.println("Device error");
}

void loop() {
  // check for reset time signal
  if (check_serial() == 'R') start_time = micros()/ 1e6;

  // send data to serial
  send_data();

  // every 100ms
  delay(100);
}

// function to check for and return signal
char check_serial() {
  if (Serial.available() > 0) return Serial.read();
}

// function to send data to serial 
void send_data() {
  // read data from sensor
  time = (micros() / 1e6) - start_time;
  aX = myIMU.readFloatAccelX();
  aY = myIMU.readFloatAccelY();
  aZ = myIMU.readFloatAccelZ();
  gX = myIMU.readFloatGyroX();
  gY = myIMU.readFloatGyroY();
  gZ = myIMU.readFloatGyroZ();

  // broadcast to serial
  Serial.print(time);
  Serial.print(", ");
  Serial.print(aX);
  Serial.print(", ");
  Serial.print(aY);
  Serial.print(", ");
  Serial.print(aZ);
  Serial.print(", ");
  Serial.print(gX);
  Serial.print(", ");
  Serial.print(gY);
  Serial.print(", ");
  Serial.println(gZ);
}
