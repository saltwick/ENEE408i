#ifndef ULTRASOUND
#define ULTRASOUND
#include <Arduino.h>

#ifdef __cplusplus
extern "C" {
#endif
#define LEFT_PING 2
#define MIDDLE_PING 8
#define RIGHT_PING 13
#define LEFT_ANGLE_TRIG A1
#define LEFT_ANGLE_ECHO A0
#define RIGHT_ANGLE_TRIG A3 
#define RIGHT_ANGLE_ECHO A2 
typedef struct {
  int pin;
  float distance;
} UltrasoundThreePin;


typedef struct {
  int echoPin;
  int trigPin;
  float distance;
} UltrasoundFourPin;


typedef struct  {
  UltrasoundThreePin left;
  UltrasoundThreePin middle;
  UltrasoundThreePin right;  
  UltrasoundFourPin left_angle;
  UltrasoundFourPin right_angle;
} Ultrasounds;


void initUltrasounds();

void evaluateDistFourPin(UltrasoundFourPin* ultrasound);

void evaluateDistThreePin(UltrasoundThreePin* ultrasound);

// Evaluate the distance for all ultrasound sensors
// for passed in stuct of sensor information
void evaluateDist(Ultrasounds* ultrasounds);
#ifdef __cplusplus
} // extern "C"
#endif
#endif 
