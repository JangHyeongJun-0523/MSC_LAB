#include "motor_driver.h"
#include <Arduino.h>

void initMotorController() {

}

// motor: LEFT (0) or RIGHT (1)
// speed: -255 ~ +255
void setMotorSpeed(int motor, int speed) {
  bool reverse = false;
  
  if (speed < 0) {
    reverse = true;
    speed = -speed;
  }
  if (speed > 255) {
    speed = 255;
  }
  
  // Left motor
  if (motor == LEFT) {
    if (!reverse) {
      analogWrite(LEFT_MOTOR_FORWARD, speed);
      analogWrite(LEFT_MOTOR_BACKWARD, 0);
    } else {
      analogWrite(LEFT_MOTOR_BACKWARD, speed);
      analogWrite(LEFT_MOTOR_FORWARD, 0);
    }
  }
  // Right motor
  else if (motor == RIGHT) {
    if (!reverse) {
      analogWrite(RIGHT_MOTOR_FORWARD, speed);
      analogWrite(RIGHT_MOTOR_BACKWARD, 0);
    } else {
      analogWrite(RIGHT_MOTOR_BACKWARD, speed);
      analogWrite(RIGHT_MOTOR_FORWARD, 0);
    }
  }
}

void setMotorSpeeds(int leftSpeed, int rightSpeed) {
  setMotorSpeed(LEFT, leftSpeed);
  setMotorSpeed(RIGHT, rightSpeed);
}
