/*
Servo check

Marcel de Vries     */
#include <Servo.h>    // used for Servo communication  

const int SelectSD      = 49;  // Micro SD card
const int SelectRTC     = 47;   // Real Time Clock
const int SelectPRS     = 45;   // Pressure Sensor
const int SelectPRS2    = 43;
const int SelectADC1    = 44;   // Temperature ADS1248 with 3x PT100
const int SelectADC2    = 46;   // Temperature ADS1248 with 3x PT100const int SelectADC2 = 6;   // Temperature ADS1248 with 3x PT100

const int SelectPack0   = 2;  // Valve Pack unit 0
const int SelectPack1   = 3;  // Valve Pack unit 1 
const int SelectPack2   = 4;  // Valve Pack unit 2
const int SelectPack3   = 5;  // Valve Pack unit 3 
const int SelectPack4   = 6;  // Valve Pack unit 3 


const int SelectPump    = 13;  // Pump unit

Servo OutServo;   // create servo object to control a servo of Output 
Servo PackServo;  // create servo object to control a servo of Pack´s

int OpenPack = 180, ClosePack = 0; //MIN 0  MAX 180
int delayServo = 1000; int NrServo = 3;

void setup()
{

 // Open serial communications and wait for port to open:
  Serial.begin(9600);
  Serial.print("Initializing ");  
  pinMode(SelectSD, OUTPUT);
  pinMode(SelectRTC, OUTPUT);
  pinMode(SelectPRS, OUTPUT);
  pinMode(SelectPRS2, OUTPUT);
  pinMode(SelectADC1, OUTPUT);
  pinMode(SelectADC2, OUTPUT);
  pinMode(SelectPack0, OUTPUT);
  pinMode(SelectPack1, OUTPUT);
  pinMode(SelectPack2, OUTPUT);
  pinMode(SelectPack3, OUTPUT);
  pinMode(SelectPack4, OUTPUT);
  
  pinMode(SelectPump, OUTPUT);

  digitalWrite(SelectSD, HIGH);
  digitalWrite(SelectRTC, HIGH);
  digitalWrite(SelectPRS, HIGH);
  digitalWrite(SelectPRS2, HIGH);
  digitalWrite(SelectADC1, HIGH);
  digitalWrite(SelectADC2, HIGH);
  digitalWrite(SelectPack0, HIGH);
  digitalWrite(SelectPack1, HIGH);
  digitalWrite(SelectPack2, HIGH);
  digitalWrite(SelectPack3, HIGH);
  digitalWrite(SelectPack4, HIGH);
  digitalWrite(SelectPump, LOW);

  Serial.println(" Servo's...");
 
}

String serialReadString() { 
  char charIn;
  String stringOut;

  stringOut = "";

  while (!(charIn == '\n')) {
    if (Serial.available() > 0) {
      charIn = Serial.read();
      if (charIn == '\n') { break; }
      else { stringOut += charIn; }
    }
  }
  return stringOut;
}

void setupServo(int SelectServo)
{
  OutServo.attach(SelectPack0);      // attaches the servo on pin  to the servo object 
  PackServo.attach(SelectServo);       // attaches the servo on pin  to the servo object 

  OutServo.write(ClosePack);    // sets the servo position according to the scaled value 
  PackServo.write(OpenPack);           // sets the servo position according to the scaled value 
  delay(500);
  OutServo.detach();               // attaches the servo on pin  to the servo object 
  //PackServo.detach();               // attaches the servo on pin  to the servo object 

  delay((delayServo-500));
  //PackServo.attach(SelectServo);      // attaches the servo on pin  to the servo object 
  PackServo.write(ClosePack);        // sets the servo position according to the scaled value 
  delay(500);
  OutServo.attach(SelectPack0);      // attaches the servo on pin  to the servo object 
  OutServo.write(OpenPack);        // sets the servo position according to the scaled value 
  delay(500);
  OutServo.detach();               // attaches the servo on pin  to the servo object 
  PackServo.detach();               // attaches the servo on pin  to the servo object 

}


void loop()
{
 String serialString; 
 Serial.println("Set delay time xxx in msec.");
 serialString = serialReadString();
 delayServo = serialString.toInt();
 Serial.print("Time set to: ");
 Serial.println(delayServo);

 Serial.println("Set servo nr.");
 serialString = serialReadString();
 NrServo = serialString.toInt();
 Serial.print("Time set to: ");
 Serial.println(NrServo);
 setupServo((NrServo+2));

}


