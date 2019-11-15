#include <stdio.h>
#include <Arduino.h>
#include "ultrasound.h"

  
void initUltrasounds() {
  pinMode(RIGHT_ANGLE_TRIG, OUTPUT);
  pinMode(RIGHT_ANGLE_ECHO, INPUT);
  pinMode(LEFT_ANGLE_TRIG, OUTPUT);
  pinMode(LEFT_ANGLE_ECHO, INPUT);
}


int sortInc(const void *cmp1, const void *cmp2) {
  float a = *((float *)cmp1);
  float b = *((float *)cmp2);
  return a - b;
}


void evaluateDistFourPin(UltrasoundFourPin* ultrasound) {
  float time_to_inches = 73.746 * 2;
    digitalWrite(ultrasound->trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(ultrasound->trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(ultrasound->trigPin, LOW);
    ultrasound->distance = pulseIn(ultrasound->echoPin, HIGH, 100000) / time_to_inches;


}


// Will take 5 readings and use the median
void evaluateDistThreePin(UltrasoundThreePin* ultrasound) {
  // According to Parallax's datasheet for the PING))), there are 73.746
  // microseconds per inch (i.e. sound travels at 1130 feet per second).
  // This gives the distance travelled by the ping, outbound and return,
  // so we multiply by 2 to get the distance of the obstacle.
  // See: http://www.parallax.com/dl/docs/prod/acc/28015-PING-v1.3.pdf
  float time_to_inches = 73.746 * 2;
    // Give a short LOW pulse beforehand to ensure a clean HIGH pulse:
    pinMode(ultrasound->pin, OUTPUT);
    // The PING))) is triggered by a HIGH pulse of 2 or more microseconds.
    digitalWrite(ultrasound->pin, HIGH);
    delayMicroseconds(3);
    digitalWrite(ultrasound->pin, LOW);
    // The same pin is used to read the signal from the PING))): a HIGH pulse
    // whose duration is the time (in microseconds) from the sending of the ping
    // to the reception of its echo off of an object.
    pinMode(ultrasound->pin, INPUT);
    // wait up to 1s (default for pulseIn)
    ultrasound->distance = pulseIn(ultrasound->pin, HIGH, 100000) / time_to_inches;
 
}


// info on ping sensor: https://www.arduino.cc/en/tutorial/ping
void evaluateDist(Ultrasounds* ultrasounds) {
  evaluateDistThreePin(&(ultrasounds->middle));
  delay(10);
  evaluateDistThreePin(&(ultrasounds->left));
  delay(10);
  evaluateDistFourPin(&(ultrasounds->left_angle));
  delay(10);
  evaluateDistThreePin(&(ultrasounds->right));
  delay(10);
  evaluateDistFourPin(&(ultrasounds->right_angle));
  delay(10);
}
