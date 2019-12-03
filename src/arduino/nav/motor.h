#ifndef MOTOR
#define MOTOR
#ifdef __cplusplus
extern "C" {
#endif

#define PWN_PIN_LEFT 9
#define INA_PIN_LEFT 10
#define INB_PIN_LEFT 11
#define EN_PIN_LEFT 12

#define PWN_PIN_RIGHT 3
#define INA_PIN_RIGHT 4
#define INB_PIN_RIGHT 5
#define EN_PIN_RIGHT 6

#define MOTOR_UPPER_LIMIT_STRAIGHT 60
#define MOTOR_LOWER_LIMIT_STRAIGHT 20

#define MOTOR_UPPER_LIMIT_TURNING 35
#define MOTOR_LOWER_LIMIT_TURNING 27

#define R_L_RATIO 1.07

#define STATIONARY 0
#define STRAIGHT 1
#define COUNTER_CLOCKWISE 2
#define CLOCKWISE 3
#define BACKWARD 4

typedef struct {
    int pwm_pin;
    int forward_pin;
    int backwards_pin;  
    int en_pin;
    bool enable;
} Motor;

typedef struct {
  Motor left;
  Motor right;
  float r_l_pwm_ratio;
  int turning_status;
} Motors;


void initMotors(Motors* motors);

void rotateClockwise(Motors* motors, int rate);

void rotateCounterClockwise(Motors* motors, int rate);

void go_straight(Motors* motors, int rate);

void go_back(Motors* motors, int rate);


void stopMotor(Motor* motor);

int threshold_Straight(int num);

int threshold_Turning(int num);

void stop(Motors* motors);

#ifdef __cplusplus
} //  close of extern "C"
#endif

#endif
