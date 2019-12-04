#include <Servo.h>


#include <stdbool.h>
#include "./ultrasound.h"
#include "./motor.h"
#include <math.h>

#define DEBUG 1
#if DEBUG
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
LiquidCrystal_I2C lcd(0x27, 20, 4);
#endif


// When uploading ensure that if using the Arduino IDE, that motor.c, motor.h, ultr   asound.c and ultrasound.h are added with
// Sketch>Add File... to have it all linked correctly

UltrasoundThreePin leftU, rightU, frontU;
UltrasoundFourPin leftAngleU, rightAngleU;

Ultrasounds ultrasounds;
////
Servo myservo;
Motor leftM;
Motor rightM;
Motors motors;
int currSpeed;
int priorPerson;
int servoPos = 90;

void setup() {
  myservo.attach(9);

#if DEBUG
  lcd.begin();
  lcd.backlight();
#endif
  Serial.begin(38400);
  // Ultrasound setup
  initUltrasounds();

  leftU = {LEFT_PING, -1};
  leftAngleU = {LEFT_ANGLE_ECHO, LEFT_ANGLE_TRIG,  -1};
  rightU = {RIGHT_PING, -1};
  rightAngleU = {RIGHT_ANGLE_ECHO, RIGHT_ANGLE_TRIG, -1};
  frontU = {MIDDLE_PING, -1};

  ultrasounds = {leftU, frontU, rightU, leftAngleU, rightAngleU};
  evaluateDist(&ultrasounds);
  //
  leftM = { PWN_PIN_LEFT,
            INA_PIN_LEFT,
            INB_PIN_LEFT,
            EN_PIN_LEFT,
            false
          };

  rightM = {  PWN_PIN_RIGHT,
              INA_PIN_RIGHT,
              INB_PIN_RIGHT,
              EN_PIN_RIGHT,
              false
           };

  motors  =  {leftM, rightM, R_L_RATIO, STATIONARY};
  initMotors(&motors);
  // Last time we saw a person where they to the left or right
  // 1 was to right
  // 0 unknown
  // -1 was to left
  priorPerson = 0;
  delay(1000);

}

void loop() {

  byte commands[6];
  if (Serial.available() >= 6) {
    Serial.print("TEST");
    Serial.readBytes(commands, 6);
    for (int i = 0; i < 6; i++) {
      Serial.println(commands[i]);
    }
    lcd.clear();
    // Process Commands
    int sum = 0;
    for (int cmd = 0; cmd < 6; cmd += 1) {
      uint16_t value = commands[cmd];
      if (value == 0 && cmd != 5) {
        sum += 1;
      }
      if (cmd == 0) {
        // Forward
#if DEBUG
        lcd.setCursor(0, 0);
        lcd.print("forward: ");
        lcd.print(value);
#endif
        if (value > 0) {
          go_straight(&motors, value);
        }
      } else if (cmd == 1) {
        // moveBackwards
        if (value > 0) {
          go_back(&motors, value);
        }
      } else if (cmd == 2) {
        // SpeedDown
      } else if (cmd == 3) {
        // Left
#if DEBUG
        lcd.setCursor(0, 1);
        lcd.print("left: ");
        lcd.print(value);
#endif
        if (value > 0 && motors.turning_status != COUNTER_CLOCKWISE) {
          rotateCounterClockwise(&motors, value);
        }
      } else if (cmd == 4) {
        // Right
#if DEBUG
        lcd.setCursor(0, 2);
        lcd.print("right: ");
        lcd.print(value);
#endif
        if (value > 0 && motors.turning_status != CLOCKWISE) {
          rotateClockwise(&motors, value);
        }
      } else if (cmd == 5) {
        myservo.write(0);
        int a = map(value, 0, 140, 0, 180);
        if (a > servoPos) {
          for (int i = servoPos; i <= a; i += 1) {
            myservo.write(i);
            delay(25);
          }
        } else if (a < servoPos) {
          for (int i = servoPos; i >= a; i -= 1) {
            myservo.write(i);
            delay(25);
          }
        }
      }
    }
    if (sum == 5) {
      stop(&motors);
    }
  }
}

void obstacleAvoidance() {
  lcdPrintUltrasound();
  if (ultrasounds.middle.distance < 10 || ultrasounds.right.distance < 10 || ultrasounds.right_angle.distance < 13 ||
      ultrasounds.left_angle.distance < 13 || ultrasounds.left.distance < 10) {
    if (motors.turning_status != COUNTER_CLOCKWISE && motors.turning_status != CLOCKWISE) {
      if (ultrasounds.right.distance > ultrasounds.left.distance) {
        rotateClockwise(&motors, .50);
      }
      else {
        rotateCounterClockwise(&motors, .50);
      }
      Serial.println(motors.turning_status);
    }
  }
  else {
    go_straight(&motors, .60);
  }


}

#if DEBUG
void lcdPrintUltrasound() {
  lcd.setCursor(2, 0);
  lcd.print("Middle: ");
  lcd.print(ultrasounds.middle.distance);
  lcd.print(" in.");
  lcd.setCursor(0, 1);
  lcd.print("L: ");
  lcd.print(ultrasounds.left.distance);
  lcd.setCursor(10, 1);
  lcd.print("LA: ");
  lcd.print(ultrasounds.left_angle.distance);
  lcd.print(" in.");
  lcd.setCursor(0, 2);
  lcd.print("R: ");
  lcd.print(ultrasounds.right.distance);
  lcd.setCursor(10, 2);
  lcd.print("RA: ");
  lcd.print(ultrasounds.right_angle.distance);
  lcd.setCursor(0, 3);
}


void lcdPrintJetsonCMD() {
  lcd.setCursor(2, 0);
  lcd.print("Middle: ");
  lcd.print(ultrasounds.middle.distance);
  lcd.print(" in.");
  lcd.setCursor(0, 1);
  lcd.print("L: ");
  lcd.print(ultrasounds.left.distance);
  lcd.setCursor(10, 1);
  lcd.print("LA: ");
  lcd.print(ultrasounds.left_angle.distance);
  lcd.print(" in.");
  lcd.setCursor(0, 2);
  lcd.print("R: ");
  lcd.print(ultrasounds.right.distance);
  lcd.setCursor(10, 2);
  lcd.print("RA: ");
  lcd.print(ultrasounds.right_angle.distance);
  lcd.setCursor(0, 3);
}

void serialPrintUltrasounds() {
  Serial.print("left : ");
  Serial.print("left : ");
  Serial.println(ultrasounds.left.distance);
  Serial.print("left_angle : ");
  Serial.println(ultrasounds.left_angle.distance);
  Serial.print("right : ");
  Serial.println(ultrasounds.right.distance);
  Serial.print("right_angle : ");
  Serial.println(ultrasounds.right_angle.distance);
  Serial.print("middle : ");
  Serial.println(ultrasounds.middle.distance);
  Serial.println("");
  Serial.println(millis());
}
#endif
