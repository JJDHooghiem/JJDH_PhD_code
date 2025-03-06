#include <SD.h>
#include <SPI.h>
#include <DS3234.h>
#include <stdlib.h>



const char airCore = 'B';
volatile boolean mode;
boolean previousMode;
byte flightST;
byte cutterON;
char charFileName[13] = "yyyymmdd.xxx";
unsigned long time = 0;

//pin declaration

const int SelectSD   = 10;  // Micro SD card
const int SelectRTC  = 9;   // Real Time Clock
const int SelectPRS  = 8;   // Pressure Sensor
const int SelectADC1 = 7;   // Temperature ADS1248 with 3x PT100
const int SelectADC2 = 6;   // Temperature ADS1248 with 3x PT100
const int SelectPRSdiff = 4;

const int btnPin  = 2;
const int Cutter  = 5;
const int VBAT    = A0;

DS3234 rtc(SelectRTC);


void setup(void)
{
  Serial.begin(9600);
  Serial.println("**************** setup   *****************");
  mode = false;
  previousMode = !mode;
  
  flightST = 0;
  cutterON = 0;
  analogWrite(VBAT, 255);                   // Power on the real time clock.            
  attachInterrupt(0, changeMode, RISING);   // <push button> for start the measurements

  pinMode(SelectSD, OUTPUT);
  pinMode(SelectPRS, OUTPUT);
  pinMode(SelectPRSdiff, OUTPUT);
  pinMode(SelectADC1, OUTPUT);
  pinMode(SelectADC2, OUTPUT);
  pinMode(Cutter, OUTPUT);

  digitalWrite(SelectSD, HIGH);
  digitalWrite(SelectPRS, HIGH);
  digitalWrite(SelectPRSdiff, HIGH);
  digitalWrite(SelectADC1, HIGH);
  digitalWrite(SelectADC2, HIGH);
  digitalWrite(Cutter, HIGH);

  SD.begin(SelectSD);

  SPIsettingsADCTS();
  setupADS1248(SelectADC1);
  setupADS1248(SelectADC2);

  SPIsettingsCOM();
}

void changeMode()
//change from mode.  
{
  mode = !mode;
}

void SPIsettingsCOM()
{ // SPI setting for 

  Serial.println("**************** SPIsettingsCOM   *****************");

  SPI.setDataMode(SPI_MODE3);
  delay(10);
  SPI.setBitOrder(MSBFIRST);
  delay(10);
  SPI.setClockDivider(SPI_CLOCK_DIV4);
  delay(10);
}

void SPIsettingsADCTS()
{  // SPI settings for the 24-bit Analog-to-Digital Converters for Temperature Sensors
  
  Serial.println("**************** SPIsettingsADCTS   *****************");
  
  SPI.setDataMode(SPI_MODE1);
  delay(10);
  SPI.setBitOrder(MSBFIRST);
  delay(10);
  SPI.setClockDivider(SPI_CLOCK_DIV8);
  delay(10);
}

void setupADS1248(int CSPin)
{
  Serial.println("**************** setupADS1248   *****************");

  digitalWrite(CSPin, LOW); // select device 
  delay(100);

  SPI.transfer(0x06); //RESET
  delay(250); //Min. 0.6 ms

  SPI.transfer(0x16); // Stop reading continuosly
  delay(100);
  
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

  digitalWrite(CSPin, HIGH); // deselect device
  delay(100);
}

String findNewFileName()
{ // Create a name with the time for logging the data in a file. 
  String fileName;
  String fileName2;
  char charFileName[13];
  byte year, month, date;

  rtc.getDateStr(year, month, date);
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
  return fileName;
}

String byte2digString(byte num)
{
  String str;
  str = "";
  if (num < 10) { str += "0"; str += String(num, DEC); }
  else {                      str += String(num, DEC); }
  return str;
}

String serialReadString()
{ 
  char charIn;
  char inData[24];
  String stringOut = "";
  int i=0;

  while (!mode) {
    if (Serial.available() > 0) {
      charIn = Serial.read();
      Serial.print(" ");
      Serial.print(charIn);
      if (charIn == '\n') { break; }
      else { Serial.print(stringOut); inData[i++]=charIn; stringOut = stringOut + charIn; }
      stringOut += charIn;
    }
  }
  for (byte x=0; x < i-2; x++)
  {  
  Serial.println(i);
  Serial.println(x);
  Serial.print(" data ");
  Serial.println(inData[x]);
  }
  Serial.println(" ");
  Serial.print(" Invooer : ");
  Serial.println(stringOut);
  return stringOut;
}


String timeString(byte year, byte month, byte date, byte hour, byte minute, byte sec)
{
  String str;

  str = ""; str += "20"; str += byte2digString(year);
  str += "-"; str += byte2digString(month);
  str += "-"; str += byte2digString(date);
  str += " "; str += byte2digString(hour);
  str += ":"; str += byte2digString(minute);
  str += ":"; str += byte2digString(sec);

  Serial.print("Set input byte to digital time! ");
  Serial.println(str);

  return str;
}

String timeString2(byte year, byte month, byte date, byte hour, byte minute, byte sec)
{
  String str;

  str = ""; str += "20"; str += byte2digString(year);
  str += ","; str += String(month, DEC);
  str += ","; str += String(date, DEC);
  str += ","; str += String(hour, DEC);
  str += ","; str += String(minute, DEC);
  str += ","; str += String(sec, DEC);

  return str;
}


void timeByte(String datiStr, byte &year, byte &month, byte &date, byte &hour, byte &minute, byte &sec)
{
  Serial.print(" data string : ");  Serial.println(datiStr);
  Serial.print(byte(datiStr.substring(2,4).toInt()));
  Serial.print(year);   Serial.print(" year ");   year = byte(datiStr.substring(2,4).toInt());     Serial.println(year);
  Serial.print(month);  Serial.print(" month ");  month = byte(datiStr.substring(5,7).toInt());    Serial.println(month);
  Serial.print(date);   Serial.print(" date ");   date = byte(datiStr.substring(8,10).toInt());    Serial.println(date);
  Serial.print(hour);   Serial.print(" hour ");   hour = byte(datiStr.substring(11,13).toInt());   Serial.println(hour);
  Serial.print(minute); Serial.print(" minute "); minute = byte(datiStr.substring(14,16).toInt()); Serial.println(minute);
  Serial.print(sec);    Serial.print(" sec ");    sec = byte(datiStr.substring(17).toInt());       Serial.println(sec);
  Serial.print(" data string : ");  Serial.println(datiStr);

  //datiStr="2015-03-06 12:45:56";

}


void getPressure(float &pressure, float &temperature, byte &stat0, byte &stat1)
{
  int byte1, byte2, byte3, byte4; 

  SPI.setClockDivider(SPI_CLOCK_DIV32);
  delay(10);

  digitalWrite(SelectPRS, LOW);
  delay(1000);
  Serial.print("byte "); Serial.print(byte1); Serial.print(" "); Serial.print(byte2);
  Serial.print(" "); Serial.print(byte3); Serial.print(" "); Serial.println(byte4);

  byte1 = SPI.transfer(0x00);  byte2 = SPI.transfer(0x00);
  byte3 = SPI.transfer(0x00);  byte4 = SPI.transfer(0x00);

  Serial.print("byte "); Serial.print(byte1); Serial.print(" "); Serial.print(byte2);
  Serial.print(" "); Serial.print(byte3); Serial.print(" "); Serial.println(byte4);
  digitalWrite(SelectPRS, HIGH);

  stat0 = (byte1 >> 6) & 1;  stat1 = (byte1 >> 7) & 1;

  byte1 &= ~(1 << 6);  byte1 &= ~(1 << 7);  byte1 <<= 8;  byte1 |= byte2;

  byte4 >>= 5;  byte3 <<= 3;  byte3 |= byte4;
  Serial.print("byte "); Serial.print(byte1); Serial.print(" "); Serial.print(byte2);
  Serial.print(" "); Serial.print(byte3); Serial.print(" "); Serial.println(byte4);
 
  pressure = (((float)byte1 - 1638.0) * (15.0 - 0.0))/(14746.0 - 1638.0) + 0.0; 
  pressure *= 68.94757;

  temperature = (float)byte3 * 200.0 / 2047.0 - 50.0; 

  SPI.setClockDivider(SPI_CLOCK_DIV4);
  delay(10);
}

float readADS1248(int RTDId)
{
  int CSPin;
  unsigned long outADC;
  byte byteMSB, byteMID, byteLSB;
  float degC;

  outADC = 0;

  if (RTDId <= 3) { CSPin = SelectADC1; }
  else { CSPin = SelectADC2; RTDId -= 3; }
  
  Serial.println(" CSPin LOW ");
  digitalWrite(CSPin, LOW);
  delay(10);
  
  // Write to IDAC1
  if (RTDId == 1)      { SPI.transfer(0x4B); SPI.transfer(0x00); SPI.transfer(0x8C); } // I1 to IEXT1, I2 OFF
  else if (RTDId == 2) { SPI.transfer(0x4B); SPI.transfer(0x00); SPI.transfer(0x2C); } // I1 to AIN2, I2 OFF
  else if (RTDId == 3) { SPI.transfer(0x4B); SPI.transfer(0x00); SPI.transfer(0x3C); } // I1 to AIN3, I2 OFF
  delay(10);
  Serial.print(RTDId);  Serial.print("   ");
  Serial.print(SPI.transfer(0x4B));  Serial.print(" 0x4B ");
  Serial.print(SPI.transfer(0x00));  Serial.print(" 0x00 ");
  if (RTDId == 1)      { Serial.print(SPI.transfer(0x8C));  Serial.println(" 0x8C ");  } // I1 to IEXT1, I2 OFF
  else if (RTDId == 2) { Serial.print(SPI.transfer(0x2C));  Serial.println(" 0x2C ");   } // I1 to AIN2, I2 OFF
  else if (RTDId == 3) { Serial.print(SPI.transfer(0x3C));  Serial.println(" 0x3C ");  } // I1 to AIN3, I2 OFF
  
  
  // Write to MUX0
  if (RTDId == 1)      { SPI.transfer(0x40); SPI.transfer(0x00); SPI.transfer(0x01); } // Burnout OFF, AIN0 +IN, AIN1 -IN
  else if (RTDId == 2) { SPI.transfer(0x40); SPI.transfer(0x00); SPI.transfer(0x25); } // Burnout OFF, AIN4 +IN, AIN5 -IN
  else if (RTDId == 3) { SPI.transfer(0x40); SPI.transfer(0x00); SPI.transfer(0x37); } // Burnout OFF, AIN6 +IN, AIN7 -IN
  delay(100);
//  delay(800);
  Serial.print(RTDId);  Serial.print("  ");
  Serial.print(SPI.transfer(0x40));  Serial.print("  ");
  Serial.print(SPI.transfer(0x00));  Serial.print("  ");
  if (RTDId == 1)      { Serial.print(SPI.transfer(0x01));  Serial.println(" 0x01 ");  } // I1 to IEXT1, I2 OFF
  else if (RTDId == 2) { Serial.print(SPI.transfer(0x25));  Serial.println(" 0x25 ");   } // I1 to AIN2, I2 OFF
  else if (RTDId == 3) { Serial.print(SPI.transfer(0x37));  Serial.println(" 0x37 ");  } // I1 to AIN3, I2 OFF
  
  SPI.transfer(0x12); // Read data once
  byteMSB = SPI.transfer(0xFF); Serial.print(byteMSB);  Serial.print(" byteMSB ");// MSB
  byteMID = SPI.transfer(0xFF); Serial.print(byteMID);  Serial.print(" byteMID ");// Mid-Byte
  byteLSB = SPI.transfer(0xFF); Serial.print(byteLSB);  Serial.print(" byteLSB ");// LSB
  outADC |= byteMSB; outADC <<= 8;  Serial.print(outADC);  Serial.print(" outADC ");
  outADC |= byteMID; outADC <<= 8;  Serial.print(outADC);  Serial.print(" outADC ");
  outADC |= byteLSB;  Serial.print(outADC);  Serial.println(" outADC ");


  degC = (2.4 / 16.0) / (pow(2.0, 23.0) - 1.0) * float(outADC); // Voltage
  degC /= 1.0e-3; // Resistance
  degC = (degC - 100.0) / (3850e-6 * 100.0); // Temperature

  Serial.print(degC);  Serial.println(" degC ");

  digitalWrite(CSPin, HIGH);
  delay(10);

  return degC;
}

void loop(void)
{

  byte year, month, date, hour, minute, sec;
  String serialString, datiStr, dataString, fileName;
  float intT, prsT, prsP, VBat, pt100t;
  char intTChar[10], prsPChar[10], prsTChar[10], VBatChar[10], pt100tChar[10];
  byte prsStat0, prsStat1;
  unsigned long dur;



  Serial.println("Give a command:");
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

    rtc.getDateStr(year, month, date);
    rtc.getTimeStr(hour);
    datiStr =timeString2(year, month, date, hour, minute, sec);

    //intT = getOneWireTemperature(insideThermometer);
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

 /*
    VBat = getVBat(VBatPin, 2739.4, 3919.0);
    dtostrf(VBat, 1, 2, VBatChar);
    dataString += ",";
    dataString += String(VBatChar);
    VBat = getVBat(VBatRelPin1, 2739.3, 3919.0);
    dtostrf(VBat, 1, 2, VBatChar);
    dataString += ",";
    dataString += String(VBatChar);
    VBat =  (VBatRelPin2, 2739.4, 3919.0);
    dtostrf(VBat, 1, 2, VBatChar);
    dataString += ",";
    dataString += String(VBatChar);
    VBat = getVBat(VBatRelPin3, 2739.3, 3919.0);
    dtostrf(VBat, 1, 2, VBatChar);
    dataString += ",";
    dataString += String(VBatChar);
*/
    SPIsettingsADCTS();
    for (int i=1; i <= 6; i++){
      pt100t = readADS1248(i);
      dtostrf(pt100t, 1, 3, pt100tChar);
      dataString += ",";
      dataString += String(pt100tChar);
    }
    SPIsettingsCOM();

/*
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
*/
    if ((flightST == 0) && (prsP < 920.0)) {      flightST = 1; }
    else if ((flightST == 1) && (prsP > 880.0)) { flightST = 2; time = millis(); }
    else if (flightST == 2)
    {
      dur = millis() - time;
      if (dur > 600000)
      {
        flightST = 3;
/*
        if (heaterON == 1)
        {
          digitalWrite(relPin1, LOW);
          heaterON = 0;
        }
*/        
        digitalWrite(Cutter, HIGH);
        cutterON = 1;
        time = millis();
      }
    }
    else if (flightST == 3)
    {
      dur = millis() - time;
      if (dur > 30000) { flightST = 0;
        digitalWrite(Cutter, LOW);
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
      Serial.println("<1> Ask time ? ");
      Serial.println("<2> Set time ! ");
      Serial.println("<3> Close value * ");
      Serial.println("<0> Quit loadmode ");
      Serial.println("Give a command:");
      previousMode = mode;
    }
    serialString = serialReadString();
    if (!mode)
    {
      Serial.println("Not mode :");
      if (serialString == "1") //?TIME
      {
        Serial.println("1) Current time:");
        for (int i=0; i <= 15; i++)
        {
          digitalWrite(SelectRTC, LOW);
          delay(10);

          Serial.print(year); Serial.print(month); Serial.println(date);
          year=0; month=0; date=0;
          rtc.getDateStr(year, month, date);
          Serial.print(year); Serial.print(month); Serial.println(date);
          rtc.getTimeStr(hour);
          Serial.println(hour);
          //minute=rtc.getTime();
          Serial.println(minute);
           datiStr =timeString(year, month, date, hour, minute, sec);
          Serial.println(datiStr);
          Serial.println(rtc.getTemp());
          delay(1000);
          digitalWrite(SelectRTC, HIGH);
          delay(10);

        }
        Serial.println("Give a command:");
      }
      else if (serialString == "3") // OPEN_VALVE
      { }
      else if (serialString == "0") // QUIT
      {
      }
      else if (serialString == "4")
      {}
      else if (serialString == "5")
      {} 
      else {  

    SPIsettingsCOM();
    //SPIsettingsADCTS();
    
          Serial.println("2) Set time (yyyy-mm-dd HH:MM:SS):");

          //serialString = serialReadString();
          Serial.print("set the time to ");
          //Serial.println(serialString);
          digitalWrite(SelectRTC, LOW);
          delay(10);

          timeByte(serialString, year, month, date, hour, minute, sec);
          
          rtc.setDate(date, month, year);
          rtc.setTime(hour, minute, sec);
          Serial.print("Time set to: ");
          Serial.println(timeString(year, month, date, hour, minute, sec));



          Serial.print(year); Serial.print(month); Serial.println(date);
          //year=0; month=0; date=0;
          Serial.print("Time set, read back settings ");
          rtc.getDateStr(year, month, date);
          Serial.print(year); Serial.print(month); Serial.println(date);
          rtc.getTimeStr(hour);
          Serial.println(hour);
          //minute=rtc.getTime();
          Serial.println(minute);
           datiStr =timeString(year, month, date, hour, minute, sec);
          Serial.println(datiStr);
          Serial.println(rtc.getTemp());
          delay(1000);
          digitalWrite(SelectRTC, HIGH);
          delay(10);

          Serial.print(" year ");
          Serial.print(year);
          Serial.println(" month ");
          Serial.println(month);
          Serial.println(" date ");
          Serial.println(date);
          Serial.println( " minute ");
          Serial.println(minute);
          Serial.println("Give a command:");
        
     } 
  
  
    }
  }
}



