/**********************************************************/
/************************** D A R *************************/ 
/**********************************************************/

// include the libraries
#include <SoftwareSerial.h>
#include <TinyGPS.h>
#include <SD.h>       // used for SD card communication
#include <SPI.h>      // used for SPI communication
#include <Servo.h>    // used for Servo communication 
#include <stdlib.h>


/* This sample code demonstrates the normal use of a TinyGPS object.
   It requires the use of SoftwareSerial, and assumes that you have a
   9600-baud serial GPS device hooked up on pins 19(rx) and 18(tx).
*/

TinyGPS gps;

static void smartdelay(unsigned long ms);
static float print_float(float val, float invalid, int len, int prec);
static void print_int(unsigned long val, unsigned long invalid, int len);
static String print_date(TinyGPS &gps);
static void print_str(const char *str, int len);

/**********************************************/
boolean debug = false; // debug mode or real mode.
/**********************************************/
Servo OutServo;   // create servo object to control a servo of Output 
Servo PackServo;  // create servo object to control a servo of Pack´s
 
const int airCore = 9; // Type airCore/Package is used.
// constant and variables
volatile boolean mode;
boolean previousMode; 
 
int pumpON = 300, delayPump = 1000, Pmax = 1300, SelectServo = 1;
int P1=200 , P2=120, P3=80, P4=30;
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

const int SelectSD   = 49;   // Micro SD card
const int SelectRTC  = 47;   // Real Time Clock
const int SelectPRS  = 45;   // Pressure Sensor
const int SelectPRS1 = 43;   // Pressure Sensor
const int SelectADC1 = 44;   // Temperature ADS1248 with 3x PT100
const int SelectADC2 = 46;   // Temperature ADS1248 with 3x PT100
//const int SelectPWM  =  3;   // Pulse Widht Mode for setting the servo.
const int SelectPack0 = 2;  // Valve Pack unit 0
const int SelectPack1 = 3;  // Valve Pack unit 1 A
const int SelectPack2 = 4;  // Valve Pack unit 2
const int SelectPack3 = 5;  // Valve Pack unit 3 
const int SelectPack4 = 6;  // Valve Pack unit 3 

const int SelectPump  = 13;   // Pump unit


int OpenPack = 180, ClosePack = 0; //MIN 0  MAX 180


void setup(void)
{
  Serial.begin(9600);
  Serial1.begin(9600);        // communication speed for GPS system.
  
  mode= false;
  previousMode = !mode;
     
  pinMode(SelectSD,   OUTPUT);
  pinMode(SelectPRS,  OUTPUT);
  pinMode(SelectPRS1, OUTPUT);
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
  digitalWrite(SelectPRS1,  HIGH);
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
  PackServo.attach(SelectServo);       // attaches the servo on pin 9 to the servo object 

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
/* Begin GPS function */ 

static void smartdelay(unsigned long ms)
{
  unsigned long start = millis();
  do { while (Serial1.available()) gps.encode(Serial1.read());
  } while (millis() - start < ms);
}

static float print_float(float val, float invalid, int len, int prec)
{
  if (val == invalid) { while (len-- > 1) Serial.print('*'); Serial.print(' '); }
  else {
    Serial.print(val, prec);
    int vi = abs((int)val);
    int flen = prec + (val < 0.0 ? 2 : 1); // . and -
    flen += vi >= 1000 ? 4 : vi >= 100 ? 3 : vi >= 10 ? 2 : 1;
    for (int i=flen; i<len; ++i) Serial.print(' ');
  }
  smartdelay(0);
  return val;
}

static void print_int(unsigned long val, unsigned long invalid, int len)
{
  char sz[32];
  if (val == invalid) strcpy(sz, "*******");
  else sprintf(sz, "%ld", val);
  sz[len] = 0;
  for (int i=strlen(sz); i<len; ++i) sz[i] = ' ';
  if (len > 0) sz[len-1] = ' ';
  Serial.print(sz);
  smartdelay(0);
}

static String print_date(TinyGPS &gps)
{
  int year;
  byte month, day, hour, minute, second, hundredths;
  unsigned long age;
  char sz[32];
  gps.crack_datetime(&year, &month, &day, &hour, &minute, &second, &hundredths, &age);
  if (age == TinyGPS::GPS_INVALID_AGE) Serial.print("********** ******** ");
  else {
    sprintf(sz, "%02d/%02d/%02d %02d:%02d:%02d ", month, day, year, hour, minute, second);
    Serial.print(sz);
  }
  print_int(age, TinyGPS::GPS_INVALID_AGE, 5);
  smartdelay(0);

  return(sz);

}

static void print_str(const char *str, int len)
{
  int slen = strlen(str);
  for (int i=0; i<len; ++i) Serial.print(i<slen ? str[i] : ' ');
  smartdelay(0);
}
/* end GPS */



void loop(void)
{
  byte hour, minute, sec;
  String serialString, datiStr, dataString;
  float intT, prsT, prsP, prsP1, VBat, pt100t;
  char prsPChar[10], TChar[10];
  String fileName;
  unsigned long dur;

  float flat, flon, falt;
  char flatChar[10], flonChar[10], faltChar[10];
  unsigned long age, GPSdate, GPStime, chars = 0;
  unsigned short sentences = 0, failed = 0;

  if (mode) {
    if (mode != previousMode) {
      Serial.println("... working in cosmacmode");
      findNewFileName();
      Serial.print("Writing to ");
      Serial.println(charFileName);
      previousMode = mode;
      File dataFile = SD.open(charFileName, FILE_WRITE);
      dataFile.println("GPS Date, Latitude, Longitude, altitude, Date, PressureOut, TemperatureOut, PressureIn, TemperatureIn, T0, T1, T2, P1, P2, P3, P4, Pmax, Pump_delay, Switch");
      dataFile.close();
    }
    
    dataString = "";
/* GPS */
//  void get_position(long *latitude, long *longitude, unsigned long *fix_age = 0);
    dataString += print_date(gps);
    dataString += ",";
    gps.f_get_position(&flat, &flon, &age);
    dtostrf(flat, 4, 6, flatChar);
    dataString += String(flatChar);
    dataString += ",";
    dtostrf(flon, 4, 6, flonChar);
    dataString += String(flonChar);
    dataString += ",";
    falt = print_float(gps.f_altitude(), TinyGPS::GPS_INVALID_F_ALTITUDE, 7, 2);
    dtostrf(falt, 4, 6, faltChar);
    
    dataString += String(print_float(gps.f_altitude(), TinyGPS::GPS_INVALID_F_ALTITUDE, 7, 2));
    dataString += ",";
    smartdelay(1000);

/*   END GPS */

    SPIsettingsCOM();
    dataString += ReadTimeDate();

    getPressure(prsP, prsT, 0);
   
    dtostrf(prsP, 1, 2, prsPChar);
    dtostrf(prsT, 1, 2, TChar);

    dataString += ",";
    dataString += String(prsPChar);
    dataString += ",";
    dataString += String(TChar);

    getPressure(prsP1, prsT, 1);
       
    dtostrf(prsP1, 1, 2, prsPChar);
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
    
    if(pumpON > 1) {
      pumpON -=1; 
    }
    else if (pumpON == 1) {
      
      pumpON= 0;
    }
    else if (prsP1 == P1) 
    {
      //set time
      //Open Servo Out
      //Start pump 
      
      
      OutServo.attach(SelectPack0);        // attaches the servo on pin 9 to the servo object 
      PackServo.attach(SelectPack1);       // attaches the servo on pin 9 to the servo object 
      digitalWrite(SelectPump, HIGH);
      Serial.println("Pumpy"); // display tekst to scherm. 
      OutServo.write(ClosePack);           // sets the servo position according to the scaled value 
      PackServo.write(OpenPack);           // sets the servo position according to the scaled value 
      PackServo.write(ClosePack);        // sets the servo position according to the scaled value
      digitalWrite(SelectPump, LOW);
      OutServo.attach(SelectPack0);      // attaches the servo on pin 9 to the servo object 
      OutServo.write(OpenPack);        // sets the servo position according to the scaled value 
      OutServo.detach();               // attaches the servo on pin 9 to the servo object 
      PackServo.detach();               // attaches the servo on pin 9 to the servo object   

    }
    else if (prsP1 == P2) 
    {
    }  
    else if (prsP1 == P3) 
    {
    }  
    else if (prsP1 == P4) 
    {
    }  
    else if (pumpON == 0) 
    {
    }  
    else if (pumpON == 1) 
    {
    }  
    else if (prsP1 <= (prsPlock-Pmax)) 
    {
      
    }  

    else { }
    
    dataString += ","; dataString += String(P1);
    dataString += ","; dataString += String(P2);
    dataString += ","; dataString += String(P3);
    dataString += ","; dataString += String(P4);
    dataString += ","; dataString += String(Pmax);
    dataString += ","; dataString += String(delayPump);
    dataString += ","; dataString += String(pumpON);
    
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
      else if (serialString == "PUMP_TIME")
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
           String serialString; 
           Serial.println("Set delay time xxx in msec.");
           serialString = serialReadString();
           int delayServoN = serialString.toInt();
           Serial.print("Time set to: ");
           Serial.println(delayServoN);

           Serial.println("Set servo nr.");
           serialString = serialReadString();
           int ServoNr = serialString.toInt();
           Serial.print("Servo set to: ");
           Serial.println(ServoNr);
           Serial.println("Set Pressure Pmax.");
           serialString = serialReadString();
           int Pmax = serialString.toInt();
           Serial.print("Pressure set to: ");
           Serial.println(Pmax);
           setupServo();

           Serial.println("Give a command:");
        }
      }
      else if (serialString == "PMAX")
      {
        Serial.println("Pressure max valve ...");
        if (!mode)
        {
           String serialString; 
           Serial.println("Set pressure mbar.");
           serialString = serialReadString();
           int Pmax = serialString.toInt();
           Serial.print("Pressure set to: ");
           Serial.println(Pmax);
           Serial.println("Give a command:");
        }
      }
      else if (serialString == "P1")
      {
        Serial.println("Pressure 1 valve ...");
        if (!mode)
        {
           String serialString; 
           Serial.println("Set pressure mbar.");
           serialString = serialReadString();
           int P1 = serialString.toInt();
           Serial.print("Pressure 1 set to: ");
           Serial.println(P1);
           Serial.println("Give a command:");
        }
      }
      else if (serialString == "P2")
      {
        Serial.println("Pressure 2 valve ...");
        if (!mode)
        {
           String serialString; 
           Serial.println("Set pressure mbar.");
           serialString = serialReadString();
           int P2 = serialString.toInt();
           Serial.print("Pressure 2 set to: ");
           Serial.println(P2);
           Serial.println("Give a command:");
        }
      }
      else if (serialString == "P3")
      {
        Serial.println("Pressure 3 valve ...");
        if (!mode)
        {
           String serialString; 
           Serial.println("Set pressure mbar.");
           serialString = serialReadString();
           P3 = serialString.toInt();
           Serial.print("Pressure 3 set to: ");
           Serial.println(P3);
           Serial.println("Give a command:");
        }
      }
      else if (serialString == "P4")
      {
        Serial.println("Pressure 4 valve ...");
        if (!mode)
        {
           String serialString; 
           Serial.println("Set pressure mbar.");
           serialString = serialReadString();
           P4 = serialString.toInt();
           Serial.print("Pressure 4 set to: ");
           Serial.println(P4);
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

