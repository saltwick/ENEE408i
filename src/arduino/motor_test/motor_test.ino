// left
int PWM1 = 11;
int inA1 = 10;
int inB1 = 12;
int EN1 = 8;

int PWM2 = 3;
int inA2 = 4;
int inB2 = 5;
int EN2 = 6;

float r_l_ratio = 1; //1.07 @ PWM_val = 64
int PWM_val = 25;

// 1 is left 2 is right
int PWM1_val = PWM_val;
int PWM2_val = PWM_val * r_l_ratio;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(inA1, OUTPUT);
  pinMode(inB1, OUTPUT);
  pinMode(PWM1, OUTPUT);
  pinMode(EN1, OUTPUT);

  pinMode(inA2, OUTPUT);
  pinMode(inB2, OUTPUT);
  pinMode(PWM2, OUTPUT);
  pinMode(EN2, OUTPUT);
    digitalWrite(EN2, HIGH);
  digitalWrite(EN1, HIGH);

}

void loop() {
  digitalWrite(inA1, HIGH);
  digitalWrite(inB1, LOW);

  digitalWrite(inA2, HIGH);
  digitalWrite(inB2, LOW);

  analogWrite(PWM1, PWM1_val);
  analogWrite(PWM2, PWM2_val);

}
