#include <OneWire.h>
#include <DallasTemperature.h>
#include <Ds3234.h>
#include <SPI.h>
#include <SD.h>
#include <stdlib.h>

const char airCore = 'B';
volatile boolean mode;
boolean previousMode;
byte heaterON;
byte flightST;
byte cutterON;
char charFileName[13] = "yyyymmdd.xxx";
unsigned long time = 0;

const int ONE_WIRE_BUS = 5;
const int TEMPERATURE_PRECISION = 12;
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature oneWireSensors(&oneWire);
DeviceAddress insideThermometer;

const int SelectSD = 10;
const int SelectRTC = 9;
const int SelectPRS = 8;
const int SelectADC1 = 7;
const int SelectADC2 = 6;
const int SelectPRSdiff = 4;

const int VBatPin = 21;
const int VBatRelPin1 = 18;
const int VBatRelPin2 = 19;
const int VBatRelPin3 = 20;

const int btnPin = 2;
const int relPin1 = 14;
const int relPin2 = 15;
const int relPin3 = 16;

Ds3234 rtc(SelectRTC);

void setup(void)
{
  Serial.begin(9600);

  mode = false;
  previousMode = !mode;
  
  flightST = 0;
  heaterON = 0;
  cutterON = 0;
   
  attachInterrupt(0, changeMode, RISING);

  pinMode(SelectSD, OUTPUT);
  pinMode(SelectPRS, OUTPUT);
  pinMode(SelectPRSdiff, OUTPUT);
  pinMode(SelectADC1, OUTPUT);
  pinMode(SelectADC2, OUTPUT);
  pinMode(relPin1, OUTPUT);
  pinMode(relPin2, OUTPUT);
  pinMode(relPin3, OUTPUT);

  digitalWrite(SelectSD, HIGH);
  digitalWrite(SelectPRS, HIGH);
  digitalWrite(SelectPRSdiff, HIGH);
  digitalWrite(SelectADC1, HIGH);
  digitalWrite(SelectADC2, HIGH);
  digitalWrite(relPin1, LOW);
  digitalWrite(relPin2, LOW);
  digitalWrite(relPin3, LOW);

  oneWireSensors.begin();
  oneWireSensors.getAddress(insideThermometer, 0);
  oneWireSensors.setResolution(insideThermometer, TEMPERATURE_PRECISION);

  SD.begin(SelectSD);

  SPIsettingsADC();
  setupADS1248(SelectADC1);
  setupADS1248(SelectADC2);

  SPIsettingsCOM();
}

void setupADS1248(int CSPin)
{

  digitalWrite(CSPin, LOW);
  delay(10);

  SPI.transfer(0x06); //RESET
  delay(250); //Min. 0.6 ms

  SPI.transfer(0x16); // Stop reading continuosly
  delay(10);
  
  SPI.transfer(0x43); // Write to SYS0
  SPI.transfer(0x00);
  SPI.transfer(0x44); // PGA 16x, 80SPS
//  SPI.transfer(0x40); // PGA 16x, 5SPS
  delay(250);
  
  SPI.transfer(0x42); // Write to MUX1
  SPI.transfer(0x00);
  SPI.transfer(0x28); // Int. oscl. ON, int. ref. ON, REF1, normal oper.
  delay(250);
  
  SPI.transfer(0x4A); // Write to IDAC0
  SPI.transfer(0x00);
  SPI.transfer(0x06); // DRDY OFF, I1&I2 1mA
  delay(250);

  digitalWrite(CSPin, HIGH);
  delay(10);
}

float readADS1248(int RTDId)
{
  int CSPin;
  unsigned long outADC;
  byte byteMSB, byteMID, byteLSB;
  float degC;

  outADC = 0;

  if (RTDId <= 3)
  {
    CSPin = SelectADC1;
  }
  else
  {
    CSPin = SelectADC2;
    RTDId -= 3;
  }
  
  digitalWrite(CSPin, LOW);
  delay(10);

  // Write to IDAC1
  if (RTDId == 1)
  {
    SPI.transfer(0x4B);
    SPI.transfer(0x00);
    SPI.transfer(0x8C); // I1 to IEXT1, I2 OFF
  }
  else if (RTDId == 2)
  {
    SPI.transfer(0x4B);
    SPI.transfer(0x00);
    SPI.transfer(0x2C); // I1 to AIN2, I2 OFF
  }
  else if (RTDId == 3)
  {
    SPI.transfer(0x4B);
    SPI.transfer(0x00);
    SPI.transfer(0x3C); // I1 to AIN3, I2 OFF
  }
  delay(10);
  
  // Write to MUX0
  if (RTDId == 1)
  {
    SPI.transfer(0x40); 
    SPI.transfer(0x00);
    SPI.transfer(0x01); // Burnout OFF, AIN0 +IN, AIN1 -IN
  }
  else if (RTDId == 2)
  {
    SPI.transfer(0x40);
    SPI.transfer(0x00);
    SPI.transfer(0x25); // Burnout OFF, AIN4 +IN, AIN5 -IN
  }
  else if (RTDId == 3)
  {
    SPI.transfer(0x40);
    SPI.transfer(0x00);
    SPI.transfer(0x37); // Burnout OFF, AIN6 +IN, AIN7 -IN
  }
  delay(100);
//  delay(800);
  
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

  digitalWrite(CSPin, HIGH);
  delay(10);

  return degC;
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

float getOneWireTemperature(DeviceAddress thermometer)
{
  float tempC;

  oneWireSensors.requestTemperatures();
  tempC = oneWireSensors.getTempC(thermometer);

  return tempC;
}

void changeMode()
{
  mode = !mode;
}

String serialReadString()
{ 
  char charIn;
  String stringOut;

  stringOut = "";

  while (!mode)
  {
    if (Serial.available() > 0)
    {
      charIn = Serial.read();
      if (charIn == '\n')
      {
        break;
      }
      else
      {
        stringOut += charIn;
      }
    }
  }
  return stringOut;
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

String timeString2(byte year, byte month, byte date, byte hour, byte minute, byte sec)
{
  String str;

  str = "";
  str += "20";
  str += byte2digString(year);
  str += ",";
  str += String(month, DEC);
  str += ",";
  str += String(date, DEC);
  str += ",";
  str += String(hour, DEC);
  str += ",";
  str += String(minute, DEC);
  str += ",";
  str += String(sec, DEC);

  return str;
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
  else
  {
    str += String(num, DEC);
  }
  return str;
}

String findNewFileName()
{
  String fileName;
  String fileName2;
  char charFileName[13];
  byte year, month, date;

  rtc.GetDate(year, month, date);
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
    if (!SD.exists(charFileName))
    {
      break;
    }
  }
  return fileName;
}

void getPressure(float &pressure, float &temperature, byte &stat0, byte &stat1)
{
  int byte1;
  int byte2;
  int byte3;
  int byte4; 

  SPI.setClockDivider(SPI_CLOCK_DIV32);
  delay(10);

  digitalWrite(SelectPRS, LOW);
  delay(10);

  byte1 = SPI.transfer(0x00);
  byte2 = SPI.transfer(0x00);
  byte3 = SPI.transfer(0x00);
  byte4 = SPI.transfer(0x00);

  digitalWrite(SelectPRS, HIGH);

  stat0 = (byte1 >> 6) & 1;
  stat1 = (byte1 >> 7) & 1;

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

  SPI.setClockDivider(SPI_CLOCK_DIV4);
  delay(10);
}

float getVBat(int Pin, float R1, float R2)
{
  int VBatInt;
  float VBat;

  VBatInt = analogRead(Pin);
  VBat = (float)VBatInt * (5.0 / 1023.0);
  VBat *= (R1 + R2) / R1;

  return VBat; 
}

void loop(void)
{

  byte year, month, date, hour, minute, sec;
  String serialString;
  String datiStr;
  String dataString;
  float intT;
  float prsT, prsP;
  char intTChar[10];
  char prsPChar[10];
  char prsTChar[10];
  byte prsStat0, prsStat1;
  String fileName;
  float VBat;
  char VBatChar[10];
  float pt100t;
  char pt100tChar[10];
  unsigned long dur;

  if (mode)
  {
    if (mode != previousMode)
    {
      Serial.println("... working in cosmacmode");
      fileName = findNewFileName();
      fileName.toCharArray(charFileName, 13);
      Serial.print("Writing to ");
      Serial.println(charFileName);
      previousMode = mode;
    }

    dataString = "";

    rtc.GetDate(year, month, date);
    rtc.GetTime(hour, minute, sec);
    datiStr =timeString2(year, month, date, hour, minute, sec);

    intT = getOneWireTemperature(insideThermometer);
    dtostrf(intT, 1, 2, intTChar);

    getPressure(prsP, prsT, prsStat0, prsStat1);
    dtostrf(prsP, 1, 2, prsPChar);
    dtostrf(prsT, 1, 2, prsTChar);

    dataString += datiStr;
    dataString += ",";
    dataString += String(intTChar);
    dataString += ",";
    dataString += String(prsPChar);
    dataString += ",";
    dataString += String(prsTChar);
    dataString += ",";
    dataString += String(prsStat1);
    dataString += ",";
    dataString += String(prsStat0);

    VBat = getVBat(VBatPin, 2739.4, 3919.0);
    dtostrf(VBat, 1, 2, VBatChar);
    dataString += ",";
    dataString += String(VBatChar);
    VBat = getVBat(VBatRelPin1, 2739.3, 3919.0);
    dtostrf(VBat, 1, 2, VBatChar);
    dataString += ",";
    dataString += String(VBatChar);
    VBat = getVBat(VBatRelPin2, 2739.4, 3919.0);
    dtostrf(VBat, 1, 2, VBatChar);
    dataString += ",";
    dataString += String(VBatChar);
    VBat = getVBat(VBatRelPin3, 2739.3, 3919.0);
    dtostrf(VBat, 1, 2, VBatChar);
    dataString += ",";
    dataString += String(VBatChar);

    SPIsettingsADC();
    for (int i=1; i <= 6; i++){
      pt100t = readADS1248(i);
      dtostrf(pt100t, 1, 3, pt100tChar);
      dataString += ",";
      dataString += String(pt100tChar);
    }
    SPIsettingsCOM();

    if ((intT < 15.0) && (heaterON == 0) && (cutterON == 0))
    {
      digitalWrite(relPin1, HIGH);
      heaterON = 1;
    }
    else if ((intT > 20.0) && (heaterON == 1))
    {
      digitalWrite(relPin1, LOW);
      heaterON = 0;
    }
    dataString += ",";
    dataString += String(heaterON);

    if ((flightST == 0) && (prsP < 920.0))
    {
      flightST = 1;
    }
    else if ((flightST == 1) && (prsP > 880.0))
    {
      flightST = 2;
      time = millis();
    }
    else if (flightST == 2)
    {
      dur = millis() - time;
      if (dur > 600000)
      {
        flightST = 3;
        if (heaterON == 1)
        {
          digitalWrite(relPin1, LOW);
          heaterON = 0;
        }
        digitalWrite(relPin2, HIGH);
        cutterON = 1;
        time = millis();
      }
    }
    else if (flightST == 3)
    {
      dur = millis() - time;
      if (dur > 30000)
      {
        flightST = 0;
        digitalWrite(relPin2, LOW);
        cutterON = 0;
      }
    }
    else
    {
    }
    dataString += ",";
    dataString += String(cutterON);
    
    Serial.println(dataString);

    File dataFile = SD.open(charFileName, FILE_WRITE);
    dataFile.println(dataString);
    dataFile.close();
    
    delay(1000);
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
          rtc.GetDate(year, month, date);
          rtc.GetTime(hour, minute, sec);
          datiStr =timeString(year, month, date, hour, minute, sec);
          Serial.println(datiStr);
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
          rtc.SetDate(year, month, date);
          rtc.SetTime(hour, minute, sec);
          Serial.print("Time set to: ");
          Serial.println(timeString(year, month, date, hour, minute, sec));
          Serial.println("Give a command:");
        }
      }
      else if (serialString == "OPEN_VALVE")
      {
        Serial.println("Opening the valve ...");
        if (!mode)
        {
          digitalWrite(relPin2, HIGH);
          delay(10000);
          digitalWrite(relPin2, LOW);
          Serial.println("Ready");
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















