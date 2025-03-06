/*
Pump test

Marcel de Vries    
 */
 

const int SelectSD      = 49;  // Micro SD card
const int SelectRTC     = 47;   // Real Time Clock
const int SelectPRS     = 45;   // Pressure Sensor
const int SelectPRS1    = 43;
const int SelectADC1    = 44;   // Temperature ADS1248 with 3x PT100
const int SelectADC2    = 46;   // Temperature ADS1248 with 3x PT100const int SelectADC2 = 6;   // Temperature ADS1248 with 3x PT100

const int SelectPump    = 13;   // Pump unit

int delayPump = 1;

void setup()
{

 // Open serial communications and wait for port to open:
  Serial.begin(9600);
  pinMode(SelectPump, OUTPUT);

  digitalWrite(SelectPump, LOW);
  
  pinMode(SelectSD, OUTPUT);
  pinMode(SelectRTC, OUTPUT);
  pinMode(SelectPRS, OUTPUT);
  pinMode(SelectPRS1, OUTPUT);
  pinMode(SelectADC1, OUTPUT);
  pinMode(SelectADC2, OUTPUT);

  digitalWrite(SelectSD, HIGH);
  digitalWrite(SelectRTC, HIGH);
  digitalWrite(SelectPRS, HIGH);
  digitalWrite(SelectPRS1, HIGH);
  digitalWrite(SelectADC1, HIGH);
  digitalWrite(SelectADC2, HIGH);
//  digitalWrite(SelectPump, LOW);

  Serial.println("Initializing Pump...");
 
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

void loop()
{
 String serialString; 
 Serial.println("Set delay time xxx in msec.");
 serialString = serialReadString();
 delayPump = serialString.toInt();
 Serial.print("Time set to: ");
 Serial.println(delayPump);

 digitalWrite(SelectPump, HIGH);
 Serial.println("..Prrrr..");
 delay(delayPump);
 digitalWrite(SelectPump, LOW);

}


