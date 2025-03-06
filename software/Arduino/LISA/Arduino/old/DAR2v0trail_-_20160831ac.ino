/**********************************************************/
/************************** D A R *************************/ 
/**********************************************************/

// include the libraries
#include <SD.h>       // used for SD card communication
#include <SPI.h>      // used for SPI communication
#include <Servo.h>    // used for Servo communication 
#include <stdlib.h>
/**********************************************/
boolean debug = false; // debug mode or real mode.
/**********************************************/
Servo OutServo;  // create servo object to control a servo of Output 
Servo PackServo;  // create servo object to control a servo of Pack´s
 
const int airCore = 6; // Type airCore is used.
// constant and variables
volatile boolean mode;
boolean previousMode; 

int cutterON = 150, delayPump = 1000; 
byte year, month, date;


char charFileName[13]; 
int TimeDate[7] = {0,0,0,0,0,0,0}; //second,minute,hour,null,day,month,year
unsigned long time = 0;

// pin description of the Adruino Nano
/*
  * SPI bus as follows:
 ** MOSI - pin 11 on Arduino Nano
 ** MISO - pin 12 on Arduino Nano
 ** CLK  - pin 13 on Arduino Nano
 ** SD   - pin 10 SD card. 
 ** RTC  - pin  9 RTC
 ** PRS -  pin  8 Pressure sensor. 
 ** ADC -  pin  7 Temperature ADS1248 with 3x PT100 
 ** ADC -  pin  6 Temperature ADS1248 with 3x PT100 
*/

const int SelectSD   = 10;   // Micro SD card
const int SelectRTC  =  9;   // Real Time Clock
const int SelectPRS  =  8;   // Pressure Sensor
const int SelectPRS1 = 18;   // Pressure Sensor
const int SelectADC1 =  7;   // Temperature ADS1248 with 3x PT100
const int SelectPack0 = 3;  // Valve Pack unit 0
const int SelectPack1 = 5;  // Valve Pack unit 1 A
const int SelectPack2 = 17;  // Valve Pack unit 2
const int SelectPack3 = 16;  // Valve Pack unit 3 
const int SelectPack4 = 15;  // Valve Pack unit 3 
const int SelectPump  = 4;   // Pump unit

int OpenPack = 180, ClosePack = 0; //MIN 0  MAX 180


void setup(void)
{
  Serial.begin(9600);
  
  mode= false;
  previousMode = !mode;
     
  pinMode(SelectSD,   OUTPUT);
  pinMode(SelectPRS,  OUTPUT);
  pinMode(SelectRTC,  OUTPUT);
  pinMode(SelectADC1, OUTPUT);
  pinMode(SelectPack0, OUTPUT);
  pinMode(SelectPack1, OUTPUT);
  pinMode(SelectPack2, OUTPUT);
  pinMode(SelectPack3, OUTPUT);
  pinMode(SelectPack4, OUTPUT);
  pinMode(SelectPump, OUTPUT);

  digitalWrite(SelectSD,   HIGH);
  digitalWrite(SelectPRS,  HIGH);
  digitalWrite(SelectRTC,  HIGH);
  digitalWrite(SelectADC1, HIGH);
  digitalWrite(SelectPump, HIGH);
  digitalWrite(SelectPack0, HIGH);
  digitalWrite(SelectPack1, HIGH);
  digitalWrite(SelectPack2, HIGH);
  digitalWrite(SelectPack3, HIGH);
  digitalWrite(SelectPack4, HIGH);
  digitalWrite(SelectPump, LOW);
   
  SD.begin(SelectSD);

  SPIsettingsADC();
  setupADS1248(SelectADC1);
  SPIsettingsCOM();
}

void setupServo()
{
  OutServo.attach(SelectPack0);      // attaches the servo on pin 9 to the servo object 
  PackServo.attach(SelectPack1);       // attaches the servo on pin 9 to the servo object 

  OutServo.write(ClosePack);    // sets the servo position according to the scaled value 
  PackServo.write(OpenPack);           // sets the servo position according to the scaled value 
  digitalWrite(SelectPump, HIGH);
  Serial.println("Pumpy");
  delay(delayPump);
  digitalWrite(SelectPump, LOW);
  PackServo.write(ClosePack);        // sets the servo position according to the scaled value 
  delay(500);
  OutServo.attach(SelectPack0);      // attaches the servo on pin 9 to the servo object 
  OutServo.write(OpenPack);        // sets the servo position according to the scaled value 
  delay(500);
  OutServo.detach();               // attaches the servo on pin 9 to the servo object 
  PackServo.detach();               // attaches the servo on pin 9 to the servo object 

}

void setupADS1248(int CSPin)
{ /* setup for the temperature sensors, ref. doc. ADS1248 */
  digitalWrite(CSPin, LOW);
  delay(10);

  SPI.transfer(0x06);        // RESET IC 
  delay(50);                // Min. 0.6 ms

  SPI.transfer(0x16);        // Stop reading continuosly
  delay(10);
  
  SPI.transfer(0x43);        // Write to SYS0
  SPI.transfer(0x00);
  SPI.transfer(0x44);        // PGA 16x, 80SPS
  delay(50);
  
  SPI.transfer(0x42);        // Write to MUX1
  SPI.transfer(0x00);
  SPI.transfer(0x28);        // Int. oscl. ON, int. ref. ON, REF1, normal oper.
  delay(50);
  
  SPI.transfer(0x4A);        // Write to IDAC0
  SPI.transfer(0x00);
  SPI.transfer(0x06);        // DRDY OFF, I1&I2 1mA
  delay(50);

  digitalWrite(CSPin, HIGH);
  delay(10);
}

void SPIsettingsADC()
{
  SPI.setDataMode(SPI_MODE1);
  delay(10);
  SPI.setBitOrder(MSBFIRST);
  delay(10);
  SPI.setClockDivider(SPI_CLOCK_DIV8);
  delay(10);
}

void SPIsettingsCOM()
{
  SPI.setDataMode(SPI_MODE3);
  delay(10);
  SPI.setBitOrder(MSBFIRST);
  delay(10);
  SPI.setClockDivider(SPI_CLOCK_DIV4);
  delay(10);
}

void findNewFileName()
{
  String fileName, fileName2;

  fileName2 = "";
  fileName2 += "20";
  fileName2 += byte2digString(year);
  fileName2 += byte2digString(month);
  fileName2 += byte2digString(date);
  fileName2 += ".";
  fileName2 += airCore;
  for (byte i=0; i < 100; i++)
  {
    fileName = "";
    fileName += fileName2;
    fileName += byte2digString(i);
    fileName.toCharArray(charFileName, 13);
    if (!SD.exists(charFileName)) { break; }
  }
}

String byte2digString(byte num)
{
  String str;
  str = "";
  if (num < 10)
  {
    str += "0";
    str += String(num, DEC);
  }
  else { str += String(num, DEC); }
  return str;
}


void getPressure(float &pressure, float &temperature, int prs)
{
  int byte1, byte2, byte3, byte4, CSPin;

  if (prs == 0) {  CSPin = SelectPRS; }
  else { CSPin = SelectPRS1; }
  
  SPI.setClockDivider(SPI_CLOCK_DIV32);
  delay(10);

  digitalWrite(CSPin, LOW);
  delay(1);
  byte1 = SPI.transfer(0x00);
  byte2 = SPI.transfer(0x00);
  byte3 = SPI.transfer(0x00);
  byte4 = SPI.transfer(0x00);

  digitalWrite(CSPin, HIGH);
  
  (byte1 >> 6) & 1;
  (byte1 >> 7) & 1;

  byte1 &= ~(1 << 6);
  byte1 &= ~(1 << 7);
  byte1 <<= 8;
  byte1 |= byte2;

  byte4 >>= 5;
  byte3 <<= 3;
  byte3 |= byte4;

  pressure = (((float)byte1 - 1638.0) * (15.0 - 0.0))/(14746.0 - 1638.0) + 0.0; 
  pressure *= 68.94757;

  temperature = (float)byte3 * 200.0 / 2047.0 - 50.0; 
  
}


float readADS1248(int RTDId) 
{ 
  unsigned long outADC = 0;
  byte byteMSB, byteMID, byteLSB;
  float degC;

  digitalWrite(SelectADC1, LOW);
  delay(10);

  // Write to IDAC1
  if (RTDId == 1) {
    SPI.transfer(0x4B);
    SPI.transfer(0x00);
    SPI.transfer(0x8C); // I1 to IEXT1, I2 OFF
  }
  else if (RTDId == 2) {
    SPI.transfer(0x4B);
    SPI.transfer(0x00);
    SPI.transfer(0x2C); // I1 to AIN2, I2 OFF
  }
  else if (RTDId == 3) {
    SPI.transfer(0x4B);
    SPI.transfer(0x00);
    SPI.transfer(0x3C); // I1 to AIN3, I2 OFF
  }
  delay(10);
  
  // Write to MUX0
  if (RTDId == 1) {
    SPI.transfer(0x40); 
    SPI.transfer(0x00);
    SPI.transfer(0x01); // Burnout OFF, AIN0 +IN, AIN1 -IN
  }
  else if (RTDId == 2) {
    SPI.transfer(0x40);
    SPI.transfer(0x00);
    SPI.transfer(0x25); // Burnout OFF, AIN4 +IN, AIN5 -IN
  }
  else if (RTDId == 3) {
    SPI.transfer(0x40);
    SPI.transfer(0x00);
    SPI.transfer(0x37); // Burnout OFF, AIN6 +IN, AIN7 -IN
  }
  delay(50);
  
  SPI.transfer(0x12); // Read data once
  byteMSB = SPI.transfer(0xFF); // MSB
  byteMID = SPI.transfer(0xFF); // Mid-Byte
  byteLSB = SPI.transfer(0xFF); // LSB
  outADC |= byteMSB;
  outADC <<= 8;
  outADC |= byteMID;
  outADC <<= 8;
  outADC |= byteLSB;

  degC = (2.4 / 16.0) / (pow(2.0, 23.0) - 1.0) * float(outADC); // Voltage
  degC /= 1.0e-3; // Resistance
  degC = (degC - 100.0) / (3850e-6 * 100.0); // Temperature

  digitalWrite(SelectADC1, HIGH);

  return degC;
}

String serialReadString() { 
  char charIn;
  String stringOut;

  stringOut = "";

  while (!mode) {
    if (Serial.available() > 0) {
      charIn = Serial.read();
      if (charIn == '\n') { break; }
      else { stringOut += charIn; }
    }
  }
  return stringOut;
}

String timeString(byte year, byte month, byte date, byte hour, byte minute, byte sec)
{
  String str;

  str = "";
  str += "20";
  str += byte2digString(year);
  str += "-";
  str += byte2digString(month);
  str += "-";
  str += byte2digString(date);
  str += " ";
  str += byte2digString(hour);
  str += ":";
  str += byte2digString(minute);
  str += ":";
  str += byte2digString(sec);

  return str;
}

void timeByte(String datiStr, byte &year, byte &month, byte &date, byte &hour, byte &minute, byte &sec)
{
  year = byte(datiStr.substring(2,4).toInt());
  month = byte(datiStr.substring(5,7).toInt());
  date = byte(datiStr.substring(8,10).toInt());
  hour = byte(datiStr.substring(11,13).toInt());
  minute = byte(datiStr.substring(14,16).toInt());
  sec = byte(datiStr.substring(17).toInt());
}

void SetTimeDate() { 
  
  for(int i=0; i<=6; i++){
    if(i==3) i++;
    int b= TimeDate[i]/10;
    int a= TimeDate[i]-b*10;
    if(i==2){
      if (b==2) b=B00000010;
      else if (b==1) b=B00000001;
    }
    TimeDate[i]= a+(b<<4);
    digitalWrite(SelectRTC, LOW);
    SPI.transfer(i+0x80); 
    SPI.transfer(TimeDate[i]);        
    digitalWrite(SelectRTC, HIGH);
  }
}

String ReadTimeDate() {
  String temp; 
  int b, i;
  char sz[32];
  
  for(i=0; i<=6;i++){
    if(i==3) i++;
    
    digitalWrite(SelectRTC, LOW);
    SPI.transfer(i+0x00); 
    unsigned int n = SPI.transfer(0x00);        
    digitalWrite(SelectRTC, HIGH);
    
    int a=n & B00001111;    
    if(i==2){ b=(n & B00110000)>>4; //24 hour mode
      if(b==B00000010)      b=20;        
      else if(b==B00000001) b=10;
      TimeDate[i]=a+b;
    }
    else if(i==4){ b=(n & B00110000)>>4; TimeDate[i]=a+b*10;}
    else if(i==5){ b=(n & B00010000)>>4; TimeDate[i]=a+b*10;}
    else if(i==6){ b=(n & B11110000)>>4; TimeDate[i]=a+b*10;}
    else{          b=(n & B01110000)>>4; TimeDate[i]=a+b*10;}
  }

  sprintf(sz, "%02d/%02d/%02d %02d:%02d:%02d ", TimeDate[6], TimeDate[5], TimeDate[4], TimeDate[2], TimeDate[1], TimeDate[0]);
  
  return(sz);
}

void loop(void)
{
  byte hour, minute, sec;
  String serialString, datiStr, dataString;
  float intT, prsT, prsP, VBat, pt100t;
  char prsPChar[10], TChar[10];
  String fileName;
  unsigned long dur;

  if (mode) {
    if (mode != previousMode) {
      Serial.println("... working in cosmacmode");
      findNewFileName();
      Serial.print("Writing to ");
      Serial.println(charFileName);
      previousMode = mode;
      File dataFile = SD.open(charFileName, FILE_WRITE);
      dataFile.println("Date, PressureOut, TemperatureOut, PressureIn, TemperatureIn, T0, T1, T2, Switch");
      dataFile.close();
    }

    dataString = "";
    dataString += ReadTimeDate();

    getPressure(prsP, prsT, 0);
   
    dtostrf(prsP, 1, 2, prsPChar);
    dtostrf(prsT, 1, 2, TChar);

    dataString += ",";
    dataString += String(prsPChar);
    dataString += ",";
    dataString += String(TChar);

    getPressure(prsP, prsT, 0);
   
    dtostrf(prsP, 1, 2, prsPChar);
    dtostrf(prsT, 1, 2, TChar);

    dataString += ",";
    dataString += String(prsPChar);
    dataString += ",";
    dataString += String(TChar);

    SPIsettingsADC();
    for (int i=1; i <= 3; i++){
      pt100t = readADS1248(i);
      dtostrf(pt100t, 1, 3, TChar);
      dataString += ",";
      dataString += String(TChar);
    }
    SPIsettingsCOM();
    
    if(cutterON > 1) {
      cutterON -=1; 
    }
    if (cutterON == 1) {     
      cutterON= 0;
    }
    if (cutterON == 68) 
    {
      digitalWrite(SelectPump, HIGH);
      Serial.println("Pumpy"); // display tekst to scherm. 
    } 
    if (cutterON == 65) 
    {
      OutServo.attach(SelectPack0);        // attaches the servo on pin 9 to the servo object 
      PackServo.attach(SelectPack1);       // attaches the servo on pin 9 to the servo object 
    } 
    if (cutterON == 60) 
    {
      OutServo.write(ClosePack);           // sets the servo position according to the scaled value 
      PackServo.write(OpenPack);           // sets the servo position according to the scaled value 
    }  
    if (cutterON == 59) 
    {
      OutServo.detach();               // attaches the servo on pin 9 to the servo object 
      PackServo.detach();               // attaches the servo on pin 9 to the servo object   
    }  

     if (cutterON == 8) 
    {
      OutServo.attach(SelectPack0);        // attaches the servo on pin 9 to the servo object 
      PackServo.attach(SelectPack1);       // attaches the servo on pin 9 to the servo object 
    } 
    if (cutterON == 6) 
    {
      OutServo.write(OpenPack);           // sets the servo position according to the scaled value 
      PackServo.write(ClosePack);           // sets the servo position according to the scaled value 
    }  
    if (cutterON == 3) 
    {
      OutServo.detach();               // attaches the servo on pin 9 to the servo object 
      PackServo.detach();               // attaches the servo on pin 9 to the servo object   
    } 
    if (cutterON == 10) 
    {
      digitalWrite(SelectPump, LOW);
    }   
    else { }
    
    dataString += ",";
    dataString += String(cutterON);
    
    Serial.println(dataString);

    File dataFile = SD.open(charFileName, FILE_WRITE);
    dataFile.println(dataString);
    dataFile.close();
    
  }
  else
  {
    if (mode != previousMode)
    {
      Serial.println("... working in loadmode");
      Serial.println("Give a command:");
      previousMode = mode;
    }
    serialString = serialReadString();
    if (!mode)
    {
      if (serialString == "?TIME")
      {
        Serial.println("Current time:");
        for (int i=0; i <= 15; i++)
        {
          Serial.println(ReadTimeDate());
          delay(1000);
        }
        Serial.println("Give a command:");
      }
      else if (serialString == "!TIME")
      {
        Serial.println("Set time (yyyy-mm-dd HH:MM:SS):");
        serialString = serialReadString();
        if (!mode)
        {
          timeByte(serialString, year, month, date, hour, minute, sec);
          TimeDate[0] = sec; //second,minute,hour,null,day,month,year
          TimeDate[1] = minute; //second,minute,hour,null,day,month,year
          TimeDate[2] = hour; //second,minute,hour,null,day,month,year
          TimeDate[4] = date; //second,minute,hour,null,day,month,year
          TimeDate[5] = month; //second,minute,hour,null,day,month,year
          TimeDate[6] = year; //second,minute,hour,null,day,month,year
    

          SetTimeDate();
          Serial.print("Time set to: ");
          //Serial.println(timeString(year, month, date, hour, minute, sec));
          Serial.println(ReadTimeDate());
          Serial.println("Give a command:");
        }
      }
      else if (serialString == "!DELAY")
      {
        Serial.println("Set delay time xxx in msec.");
        serialString = serialReadString();
        if (!mode)
        {
          delayPump = serialString.toInt();
          Serial.print("Time set to: ");
          //Serial.println(timeString(year, month, date, hour, minute, sec));
          Serial.print(delayPump);
          Serial.println(" mSec.");
          Serial.println("Give a command:");
        }
      }
      else if (serialString == "OPEN_VALVE")
      {
        Serial.println("Opening the valve ...");
        if (!mode)
        {
           setupServo();
           Serial.println("Give a command:");
        }
      }
      else if (serialString == "QUIT")
      {
        Serial.println("Quitting ...");
        mode = true;
      }
      else
      {
        Serial.print("Unknown command: ");
        Serial.println(serialString);
      }
    }
  }
}

