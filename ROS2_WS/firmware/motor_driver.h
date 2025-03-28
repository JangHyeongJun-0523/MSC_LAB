#ifndef MOTOR_DRIVER_H
#define MOTOR_DRIVER_H

/***************************************************************
   Motor driver function definitions for L298N
   (Using encoder-less DC motors)
   ***************************************************************/

#define LEFT_MOTOR_FORWARD   9
#define LEFT_MOTOR_BACKWARD  10
#define RIGHT_MOTOR_FORWARD  5
#define RIGHT_MOTOR_BACKWARD 6
#define LEFT  0
#define RIGHT 1

void initMotorController();
void setMotorSpeed(int motor, int speed);
void setMotorSpeeds(int leftSpeed, int rightSpeed);

#endif
