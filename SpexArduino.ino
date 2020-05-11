/*******************************
 * Author: Thy Doan Mai Le
 * Date created: 4/2/2019
 * 
 */


volatile int stepsTaken = 0;
int stepPin = 2; 
int scanPin = 4;
//int dirPin = 3;
int clrPin = 11;
int clkPin = 6;

//volatile unsigned int step2Convert = 400;
//int convertRate = 1;
//int totalSteps = 400;

char usrInput = "";
volatile int voltage = 0;
bool start = false;

//determining the rate at which ADC conversions are don

void setup() {
  // put your setup code here, to run once:
  Serial.begin(250000);

  pinMode(clkPin, OUTPUT);
  pinMode(clrPin, OUTPUT);
  pinMode(stepPin, INPUT_PULLUP);
 // pinMode(dirPin, INPUT_PULLUP);
  pinMode(scanPin, INPUT_PULLUP);
  
 // pinMode(A0, INPUT);
  analogReference(DEFAULT);
  
  attachInterrupt(digitalPinToInterrupt(stepPin), count, FALLING);

  Serial.write("SPEX");
  digitalWrite(clrPin, HIGH);
  digitalWrite(clkPin, LOW);
  digitalWrite(13, LOW);
}



void count(){
    if(digitalRead(scanPin) == LOW){

      //Serial.println(stepsTaken);
      stepsTaken++;
      
      if(stepsTaken == 400){
       
       digitalWrite(clkPin, HIGH);
       voltage = analogRead(A0);
        Serial.println(voltage);
       digitalWrite(clkPin, LOW);
       // voltage = analogRead(A0);
        
        digitalWrite(clrPin, LOW);
        digitalWrite(clrPin, HIGH);
      //  Serial.println(voltage);

      stepsTaken = 0;
      }

      
  } 
}

void loop() {
  
  //echo routine
  if(Serial.available()){
    usrInput = Serial.read();

    if(usrInput == 'g'){
      start = true;
      usrInput = "";
    }
    else if(usrInput == 's'){
      start = false;
      usrInput = "";
    }
  }
 
}
