// 모터 제어 핀 설정
#define LEFT_MOTOR_FORWARD 9
#define LEFT_MOTOR_BACKWARD 10
#define RIGHT_MOTOR_FORWARD 5
#define RIGHT_MOTOR_BACKWARD 6

void setup() {
  // 시리얼 모니터 시작
  Serial.begin(9600);  // 시리얼 모니터의 baud rate를 9600으로 설정
  delay(5000); 

  // 모터 제어 핀을 출력으로 설정
  pinMode(LEFT_MOTOR_FORWARD, OUTPUT);
  pinMode(LEFT_MOTOR_BACKWARD, OUTPUT);
  pinMode(RIGHT_MOTOR_FORWARD, OUTPUT);
  pinMode(RIGHT_MOTOR_BACKWARD, OUTPUT);

  // 모터를 5초 동안 느리게 직진 시킴
  Serial.println("Starting motor movement...");
  driveForward();  // 모터를 전진
  Serial.println("Motor is moving forward");
  delay(5000); // 5초 직진
  Serial.println("Stopping motor...");
  stopMotors(); // 정지
  Serial.println("Motor stopped.");
}

void loop() {
  // loop()는 비워 두어도 됩니다. setup()에서 동작하도록 설정했으므로 반복적으로 실행되지 않음.
}

// 직진 함수 (속도를 낮추어 실행)
void driveForward() {
  // 왼쪽 모터와 오른쪽 모터가 전진하는 명령을 보냄
  Serial.println("Setting motors to move forward with reduced speed...");
  analogWrite(LEFT_MOTOR_FORWARD, 110);  // 왼쪽모터
  digitalWrite(LEFT_MOTOR_BACKWARD, LOW);
  analogWrite(RIGHT_MOTOR_FORWARD, 90);  // 오른쪽 모터
  digitalWrite(RIGHT_MOTOR_BACKWARD, LOW);
  Serial.println("Motors set to move forward at reduced speed.");
}

// 모터 정지 함수
void stopMotors() {
  // 모터를 정지시킴
  Serial.println("Turning off motors...");
  digitalWrite(LEFT_MOTOR_FORWARD, LOW);
  digitalWrite(LEFT_MOTOR_BACKWARD, LOW);
  digitalWrite(RIGHT_MOTOR_FORWARD, LOW);
  digitalWrite(RIGHT_MOTOR_BACKWARD, LOW);
  Serial.println("Motors turned off.");
}
