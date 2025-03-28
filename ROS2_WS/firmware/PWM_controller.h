#ifndef MOTOR_CONTROL_H
#define MOTOR_CONTROL_H

#define MAX_PWM 255

#define LEFT_MOTOR_FORWARD   9
#define LEFT_MOTOR_BACKWARD  10
#define RIGHT_MOTOR_FORWARD  5
#define RIGHT_MOTOR_BACKWARD 6
#define LEFT  0
#define RIGHT 1

// Send PWM Signals to both motors
void setMotorSpeeds(int leftSpeed, int rightSpeed) {
  // Left motor
  if(leftSpeed >= 0) {
    analogWrite(LEFT_MOTOR_FORWARD, leftSpeed);
    digitalWrite(LEFT_MOTOR_BACKWARD, LOW);
  } else {
    analogWrite(LEFT_MOTOR_FORWARD, 0);
    analogWrite(LEFT_MOTOR_BACKWARD, -leftSpeed);
  }
  // Right motor
  if(rightSpeed >= 0) {
    analogWrite(RIGHT_MOTOR_FORWARD, rightSpeed);
    digitalWrite(RIGHT_MOTOR_BACKWARD, LOW);
  } else {
    analogWrite(RIGHT_MOTOR_FORWARD, 0);
    analogWrite(RIGHT_MOTOR_BACKWARD, -rightSpeed);
  }
}

#endif