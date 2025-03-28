#include "motor_driver.h"

void setup() {
  Serial.begin(57600); // ROS2와의 통신을 위한 시리얼 속도 설정
  initMotorController(); // 모터 컨트롤러 초기화
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read(); // ROS2로부터 명령 수신

    int leftSpeed = 0;
    int rightSpeed = 0;

    // 수신한 명령에 따라 모터 속도 설정
    switch (command) {
      case 'w': // 전진
        leftSpeed = 150;
        rightSpeed = 150;
        break;
      case 'x': // 후진
        leftSpeed = -150;
        rightSpeed = -150;
        break;
      case 'a': // 좌회전
        leftSpeed = -150;
        rightSpeed = 150;
        break;
      case 'd': // 우회전
        leftSpeed = 150;
        rightSpeed = -150;
        break;
      case 's': // 정지
        leftSpeed = 0;
        rightSpeed = 0;
        break;
    }

    setMotorSpeeds(leftSpeed, rightSpeed); // 모터 속도 적용
  }
}