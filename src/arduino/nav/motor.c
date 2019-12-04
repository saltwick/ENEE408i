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
    analogWrite(motor->pwm_pin, fabs(speed));
  } else {
    stopMotor(motor);
  }
}

void rotateClockwise(Motors* motors, int rate) {
  motors->turning_status = CLOCKWISE;
  int speed = threshold_Turning(rate);
  setSpeed(&(motors->left), speed);
  setSpeed(&(motors->right), ceil(-speed * motors->r_l_pwm_ratio));
}

void rotateCounterClockwise(Motors* motors, int rate) {
  motors->turning_status = COUNTER_CLOCKWISE;
  int speed = threshold_Turning(rate);
  setSpeed(&(motors->left), -speed);
  setSpeed(&(motors->right), ceil(speed * motors->r_l_pwm_ratio));
}

void stop(Motors* motors) {
  motors->turning_status = STATIONARY;

  setSpeed(&(motors->left), 0);
  setSpeed(&(motors->right), 0);
}

void go_straight(Motors* motors, int rate) {
    
  motors->turning_status = STRAIGHT;
  int speed = threshold_Straight(rate);
  setSpeed(&(motors->left), speed);
  setSpeed(&(motors->right), ceil(speed * motors->r_l_pwm_ratio));
}

void go_back(Motors* motors, int rate) {
  motors->turning_status = BACKWARD;
  int speed = threshold_Straight(rate);
  setSpeed(&(motors->left), ceil(-speed));
  setSpeed(&(motors->right), ceil(-speed * motors->r_l_pwm_ratio));
}

/*
differentialClockwise(float rate, float radius) {

}

differentialCounterClockwise(float rate, float radius ) {

}
*/


int threshold_Straight(int speed) {
// Make sure speed is in bounds 
  if (speed < 0) {
    if (speed < -MOTOR_UPPER_LIMIT_STRAIGHT) {
      speed = -MOTOR_UPPER_LIMIT_STRAIGHT;
    }
    if (speed > -MOTOR_LOWER_LIMIT_STRAIGHT) {
      speed = -MOTOR_LOWER_LIMIT_STRAIGHT;
    }
  } 
  else if (speed > 0) {
    if (speed > MOTOR_UPPER_LIMIT_STRAIGHT) {
      speed = MOTOR_UPPER_LIMIT_STRAIGHT;
    }
    if (speed < MOTOR_LOWER_LIMIT_STRAIGHT) {
      speed = MOTOR_LOWER_LIMIT_STRAIGHT;
    }
  }
  return ceil(speed);
  
}

int threshold_Turning(int speed) {
  // Make sure speed is in bounds 
  if (speed < 0) {
    if (speed < -MOTOR_UPPER_LIMIT_TURNING) {
      speed = -MOTOR_UPPER_LIMIT_TURNING;
    }
    if (speed > -MOTOR_LOWER_LIMIT_TURNING) {
      speed = -MOTOR_LOWER_LIMIT_TURNING;
    }
  } 
  else if (speed > 0) {
    if (speed > MOTOR_UPPER_LIMIT_TURNING) {
      speed = MOTOR_UPPER_LIMIT_TURNING;
    }
    if (speed < MOTOR_LOWER_LIMIT_TURNING) {
      speed = MOTOR_LOWER_LIMIT_TURNING;
    }
  }
  return ceil(speed);
}
void stopMotor(Motor* motor) {
  motor->enable = false;
  digitalWrite(motor->en_pin, LOW);
}
