#include <stdbool.h>
#include <Arduino.h>
#include "motor.h"

void initMotors(Motors* motors) {
  pinMode(motors->left.forward_pin, OUTPUT);
  pinMode(motors->left.backwards_pin, OUTPUT);
  pinMode(motors->left.pwm_pin, OUTPUT);
  pinMode(motors->left.en_pin, OUTPUT);

  pinMode(motors->right.forward_pin, OUTPUT);
  pinMode(motors->right.backwards_pin, OUTPUT);
  pinMode(motors->right.pwm_pin, OUTPUT);
  pinMode(motors->right.en_pin, OUTPUT);

  digitalWrite(motors->right.en_pin, HIGH);
  digitalWrite(motors->left.en_pin, HIGH);
}

void setSpeed(Motor* motor, int speed) {
  
 // Make sure speed is in bounds 
  if (speed < 0) {
    if (speed < -MOTOR_UPPER_LIMIT) {
      speed = -MOTOR_UPPER_LIMIT;
    }
    if (speed > -MOTOR_LOWER_LIMIT) {
      speed = -MOTOR_LOWER_LIMIT;
    }
  } 
  else if (speed > 0) {
    if (speed > MOTOR_UPPER_LIMIT) {
      speed = MOTOR_UPPER_LIMIT;
    }
    if (speed < MOTOR_LOWER_LIMIT) {
      speed = MOTOR_LOWER_LIMIT;
    }
  }

  if (speed != 0 && !(motor->enable)) {
    motor->enable = true;
    digitalWrite(motor->en_pin, HIGH);
  }
  if (speed < 0) {
    digitalWrite(motor->forward_pin, LOW);
    digitalWrite(motor->backwards_pin, HIGH);
    analogWrite(motor->pwm_pin, fabs(speed));
  } else if (speed > 0) {
    digitalWrite(motor->forward_pin, HIGH);
    digitalWrite(motor->backwards_pin, LOW);
    analogWrite(motor->pwm_pin, speed);
  } else {
    stopMotor(motor);
  }
}

void rotateClockwise(Motors* motors, float rate) {
  motors->turning_status = CLOCKWISE;
  setSpeed(&(motors->left), ceil(MOTOR_UPPER_LIMIT * rate));
  setSpeed(&(motors->right), ceil(-MOTOR_UPPER_LIMIT * rate * motors->r_l_pwm_ratio));
}

void rotateCounterClockwise(Motors* motors, float rate) {
  motors->turning_status = COUNTER_CLOCKWISE;
  setSpeed(&(motors->left), ceil(-MOTOR_UPPER_LIMIT * rate));
  setSpeed(&(motors->right), ceil(MOTOR_UPPER_LIMIT * rate * motors->r_l_pwm_ratio));
}

void go_straight(Motors* motors, float rate) {
  motors->turning_status = STRAIGHT;
  setSpeed(&(motors->left), ceil(MOTOR_UPPER_LIMIT * rate));
  setSpeed(&(motors->right), ceil(MOTOR_UPPER_LIMIT * rate * motors->r_l_pwm_ratio));
}

/*
differentialClockwise(float rate, float radius) {

}

differentialCounterClockwise(float rate, float radius ) {

}
*/

void stopMotor(Motor* motor) {
  motor->enable = false;
  digitalWrite(motor->en_pin, LOW);
}
