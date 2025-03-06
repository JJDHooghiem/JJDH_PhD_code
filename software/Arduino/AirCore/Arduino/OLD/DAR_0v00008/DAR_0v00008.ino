/**********************************************************/
/************************** D A R *************************/ 
/**********************************************************/

// include the libraries
#include <SD.h>       // used for SD card communication
#include <SPI.h>      // used for SPI communication
#include <DS3234.h>   // used for Real Time Clock communication (IC:ds3234)

/**********************************************/
boolean debug = true; // debug mode or real mode.
/**********************************************/

const int airCore = 3; // Type airCore is used.
char charFileName[20];

File myFile;

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
const int SelectSD   = 10;  // Micro SD card
const int SelectRTC  = 9;   // Real Time Clock
const int SelectPRS  = 8;   // Pressure Sensor
const int SelectADC1 = 7;   // Temperature ADS1248 with 3x PT100
const int SelectADC2 = 6;   // Temperature ADS1248 with 3x PT100
const int SelectGPSV = 5;   // Power supply for GPS unit
const int SelectGPSR = 4;   // TX for GPS unit 
const int SelectGPST = 3;   // RX for GPS unit
const int AutoValve  = A3;  // Automatic valve, cutter for closing the coil.  

// constant and variables
volatile boolean mode;
boolean previousMode; 
float prsT, prsP, sumP = 0.0, avgP = 99999, P0 = 0.0, dP, pt100t;
byte prsStat0, prsStat1, cutterON = 0, flightST = 0;
char prsPChar[10], prsTChar[10], pt100tChar[10];
int year=15, month=06, day=01, hour, minute, second;
int wait = 10, avg, checkcnt = 3;
unsigned long time = 0;
String serialString;
int TimeDate[7] = {0,0,0,0,0,0,0}; //second,minute,hour,null,day,month,year

void setup(void)
{
  Serial.begin(9600);

  Serial.println("**** CLOCK SETTING ****");
  Serial.println("Set Year (yy): ");
  serialReadClockSetting(6);              //second,minute,hour,null,day,month,year	
  Serial.println("Set Month [01-12](mm): ");
  serialReadClockSetting(5);              //second,minute,hour,null,day,month,year	
  Serial.println("Set day (dd)[1-31]: ");
  serialReadClockSetting(4);              //second,minute,hour,null,day,month,year	
  Serial.println("Set hour (HH) [0-24]: ");
  serialReadClockSetting(2);              //second,minute,hour,null,day,month,year	
  Serial.println("Set minute (MM) [0-59]: ");
  serialReadClockSetting(1);              //second,minute,hour,null,day,month,year	
  Serial.println("Set seconde (SS) [0-59]: ");
  serialReadClockSetting(0);              //second,minute,hour,null,day,month,year	
  
  Serial.print("Time set to: ");

  pinMode(SelectSD,   OUTPUT);
  pinMode(SelectPRS,  OUTPUT);
  pinMode(SelectRTC,  OUTPUT);
  pinMode(SelectADC1, OUTPUT);
  pinMode(SelectADC2, OUTPUT);
  pinMode(AutoValve,  OUTPUT);

  digitalWrite(SelectSD,   HIGH);
  digitalWrite(SelectPRS,  HIGH);
  digitalWrite(SelectRTC,  HIGH);
  digitalWrite(SelectADC1, HIGH);
  digitalWrite(SelectADC2, HIGH);
  analogWrite(AutoValve,  0);

  SPI.begin();
  SPIsettingsCOM();                               // Set COM settings for SPI communication 
  RTC_init();                                     // initialize Real Time Clock    
  SetTimeDate();                                  // day(1-31), month(1-12), year(0-99), hour(0-23), minute(0-59), second(0-59)
  checkClock();                                   // CHECK THE TIME AND DATE OF THE CLOCK OF THE DATALOGGER

  if (!SD.begin(SelectSD)) { Serial.println("initialization failed!"); return;  }
  checkDatalogFileName();
  checkPressure();                                // CHECK THE AUTOMATICVALVE OF THE DATALOGGER
  SPIsettingsADC(); 
  setupADS1248(SelectADC1);                       // SETUP ads1248
  setupADS1248(SelectADC2);                       // 
  checkTemperature();                             // CHECK THE AUTOMATICVALVE OF THE DATALOGGER
  SPIsettingsCOM();                               // Set COM settings for SPI communication 
  checkAutomaticValve();                          // CHECK THE AUTOMATICVALVE OF THE DATALOGGER
  
}

void SPIsettingsADC()
{
  SPI.setDataMode(SPI_MODE1);
  delay(wait);
  SPI.setBitOrder(MSBFIRST);
  delay(wait);
  SPI.setClockDivider(SPI_CLOCK_DIV8);
  delay(wait);
}

void SPIsettingsCOM()
{
  SPI.setDataMode(SPI_MODE3);
  delay(wait);
  SPI.setBitOrder(MSBFIRST);
  delay(wait);
  SPI.setClockDivider(SPI_CLOCK_DIV4);
  delay(wait);
}

void SPIsettingsPRS()
{
  SPI.setClockDivider(SPI_CLOCK_DIV32);
  delay(wait);
}

void setupADS1248(int CSPin)
{ /* setup for the temperature sensors, ref. doc. ADS1248 */
  digitalWrite(CSPin, LOW);
  delay(wait);

  SPI.transfer(0x06);        // RESET IC 
  delay(600);                // Min. 0.6 ms

  SPI.transfer(0x16);        // Stop reading continuosly
  delay(wait);
  
  SPI.transfer(0x43);        // Write to SYS0
  SPI.transfer(0x00);
  SPI.transfer(0x44);        // PGA 16x, 80SPS
//  SPI.transfer(0x40);        // PGA 16x, 5SPS
  delay(250);
  
  SPI.transfer(0x42);        // Write to MUX1
  SPI.transfer(0x00);
  SPI.transfer(0x28);        // Int. oscl. ON, int. ref. ON, REF1, normal oper.
  delay(250);
  
  SPI.transfer(0x4A);        // Write to IDAC0
  SPI.transfer(0x00);
  SPI.transfer(0x06);        // DRDY OFF, I1&I2 1mA
  delay(250);

  digitalWrite(CSPin, HIGH);
  delay(wait);
}

float readADS1248(int RTDId)
{ 
  int CSPin;
  unsigned long outADC = 0;
  byte byteMSB, byteMID, byteLSB;
  float degC;

  if (RTDId <= 3) {  CSPin = SelectADC1; }
  else { RTDId -= 3; CSPin = SelectADC2; }
  
  digitalWrite(CSPin, LOW);
  delay(200);

  // Write to IDAC1
  SPI.transfer(0x4B);
  SPI.transfer(0x00);
  
  if (RTDId == 1)      { SPI.transfer(0x8C); } // I1 to IEXT1, I2 OFF 
  else if (RTDId == 2) { SPI.transfer(0x2C); } // I1 to AIN2, I2 OFF
  else if (RTDId == 3) { SPI.transfer(0x3C); } // I1 to AIN3, I2 OFF
  delay(250);
  // Write to MUX0
  SPI.transfer(0x40); 
  SPI.transfer(0x00);
  if (RTDId == 1)      { SPI.transfer(0x01); }// Burnout OFF, AIN0 +IN, AIN1 -IN
  else if (RTDId == 2) { SPI.transfer(0x25); }// Burnout OFF, AIN4 +IN, AIN5 -IN
  else if (RTDId == 3) { SPI.transfer(0x37); }// Burnout OFF, AIN6 +IN, AIN7 -IN
  delay(250);
  
  SPI.transfer(0x12);           // Read data once
  byteMSB = SPI.transfer(0xFF); // MSB
  byteMID = SPI.transfer(0xFF); // Mid-Byte
  byteLSB = SPI.transfer(0xFF); // LSB
  outADC |= byteMSB;
  outADC <<= 8;
  outADC |= byteMID;
  outADC <<= 8;
  outADC |= byteLSB;

  degC = (2.4 / 16.0) / (pow(2.0, 23.0) - 1.0) * float(outADC); // Voltage
  degC /= 1.0e-3;                                               // Resistance
  degC = (degC - 100.0) / (3850e-6 * 100.0);                    // Temperature

  digitalWrite(CSPin, HIGH);
  delay(wait);

  return degC;
}

void getPressure(float &pressure, float &temperature, byte &stat0, byte &stat1)
{
  SPI.setClockDivider(SPI_CLOCK_DIV32);

  digitalWrite(SelectPRS,LOW);
  delay(wait);
 
  int inByte_1 = SPI.transfer(0x00);
  int inByte_2 = SPI.transfer(0x00);
  int inByte_3 = SPI.transfer(0x00);
  int inByte_4 = SPI.transfer(0x00);
 
  if(debug) { // debug mode or real mode.
     Serial.print("Byte_1 = ");Serial.print(inByte_1,DEC);Serial.print(" ");
     Serial.print("Byte_2 = ");Serial.print(inByte_2,DEC);Serial.print(" ");
     Serial.print("Byte_3 = ");Serial.print(inByte_3,DEC);Serial.print(" ");
     Serial.print("Byte_4 = ");Serial.print(inByte_4,DEC);Serial.print(" ");
  }
  float psi = inByte_1<<8|inByte_2;
  psi = (psi*5)/16384;
  if(debug) { Serial.print("PRES = ");Serial.print(psi);Serial.print(" "); }
  inByte_3 = inByte_3<<3;
  float realTemp = ((float)inByte_3*200/2047)-50;
  if(debug) { Serial.print("Temp[C]= ");Serial.print(realTemp);Serial.print("\n"); }
   
  stat0 = (inByte_1 >> 6) & 1;
  stat1 = (inByte_1 >> 7) & 1;
  if(debug) { Serial.print("STAT = ");Serial.print(stat0);Serial.print(" ");Serial.println(stat1); }

  inByte_1 &= ~(1 << 6);
  inByte_1 &= ~(1 << 7);
  inByte_1 <<= 8;
  inByte_1 |= inByte_2;

  inByte_4 >>= 5;
//  inByte_3 <<= 3;
  inByte_3 |= inByte_4;

  pressure = (((float)inByte_1 - 1638.0) * (15.0 - 0.0))/(14746.0 - 1638.0) + 0.0; 
  pressure *= 68.94757;
  if(debug) { Serial.print("pressure = "); Serial.println(pressure); }
  temperature = (float)inByte_3 * 200.0 / 2047.0 - 50.0; 
  if(debug) { Serial.print("temperature[C]= ");Serial.print(temperature);Serial.print("\n"); }
  
  digitalWrite(SelectPRS,HIGH);
  
  SPI.setClockDivider(SPI_CLOCK_DIV4);
  delay(wait); 
}
/* ***************** */
/*  CLOCK FUNCTION   */
/* ***************** */
int RTC_init(){ 
  digitalWrite(SelectRTC, LOW);  
  delay(wait);
  SPI.transfer(0x8E);
  SPI.transfer(0x60);           //60= disable Osciallator and Battery SQ wave @1hz, temp compensation, Alarms disabled
  digitalWrite(SelectRTC, HIGH);
  delay(wait);
}

int SetTimeDate() { 
  
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

void serialReadClockSetting(int set)
{ 
  char charIn = 0;
  String stringOut = "";

  while (charIn != '\n') {
    if (Serial.available() > 0) { 
      charIn = Serial.read();
      stringOut += charIn;
    }
  }
  TimeDate[set] = stringOut.toInt();
  Serial.println(" => ");
}

void checkClock() {
  for (int i=0; i <= 15; i++)
  {
     Serial.println(ReadTimeDate());
     delay(1000);
  }
}

/* ***************** */
/* FILENAME FUNCTION */
/* ***************** */

void checkDatalogFileName(){
  Serial.print("Initializing SD card...");
  for (byte i=0; i < 100; i++)
  {
    sprintf(charFileName, "%02d%02d%02d%02d.csv", airCore, TimeDate[5], TimeDate[4], i);
    if (!SD.exists(charFileName)) { break; }
  }
  Serial.println("Creating file : ");
  Serial.println(charFileName);
  Serial.println("Opening file : " );
  
  myFile = SD.open(charFileName, FILE_WRITE);
  
  // if the file opened okay, write to it:
  if (myFile) {
    Serial.print("Writing to .. ");
    myFile.println("Date, Time, Pressure, Tin, Stat1, Stat0, T1, T2, T3, T4, T5, T6, Burn, FlightST");
    // close the file:
    myFile.close();
    Serial.println(" ...done.");
  } else {
    // if the file didn't open, print an error:
    Serial.print("error opening : ");
    Serial.println(charFileName);
  }
  // re-open the file for reading:
  myFile = SD.open(charFileName);
  if (myFile) {
    Serial.print("Open file : ");
    Serial.println(charFileName);
    // read from the file until there's nothing else in it:
    while (myFile.available()) { Serial.write(myFile.read()); }
    myFile.close();    // close the file:
  } else {             // if the file didn't open, print an error:
    Serial.print("error opening : ");
    Serial.println(charFileName);
  }
  Serial.print("Initializing SD card done.");
}

void checkTemperature(){
  SPIsettingsADC(); 
  Serial.println("Temperature : ");  //Temperature reading 

  for (int i=1; i <= 6; i++){
     pt100t = readADS1248(i);
     dtostrf(pt100t, 1, 3, pt100tChar);
     if(debug) {
        Serial.print (i);
        Serial.print (" , ");
        Serial.println(pt100tChar);
     }
  } 
  Serial.println("-- Temperature reading done. -- ");  //Temperature reading 
}

void checkPressure(){
  Serial.println("Pressure : ");
  getPressure(prsP, prsT, prsStat0, prsStat1);
  Serial.print("P = ");      Serial.print(prsP);
  Serial.print(" T = ");     Serial.println(prsT);
  Serial.print("Stat0 = ");  Serial.print(prsStat0);
  Serial.print(" Stat1 = "); Serial.println(prsStat1);
}

void checkAutomaticValve(){

  Serial.println("Opening the valve ...");
  if (!mode) {
     analogWrite(AutoValve, 255);
     delay(7000);
     analogWrite(AutoValve, 0);
     Serial.println("Ready");
     }
  Serial.println("------ done. ------ ");  //Temperature reading 
}

void loop(void) 
{ // standard setting SPI_CLOCK_DIV4 MODE3
  String dataString;//, fileName;
//  unsigned long dur;


    dataString = "test,";
/*    // Time reading 
    dataString += ReadTimeDate();
    // Pressure and temperatuur
    getPressure(prsP, prsT, prsStat0, prsStat1);
    dtostrf(prsP, 1, 2, prsPChar);
    dtostrf(prsT, 1, 2, prsTChar);
    dataString += ",";  dataString += String(prsPChar);
    dataString += ",";  dataString += String(prsTChar);
    dataString += ",";  dataString += String(prsStat1);
    dataString += ",";  dataString += String(prsStat0);
*/     
    //Temperature reading 
    SPIsettingsADC(); 
    for (int i=1; i <= 6; i++){
      pt100t = readADS1248(i);
      dtostrf(pt100t, 1, 3, pt100tChar);
      if(debug) {
         Serial.print (i);
         Serial.print (" , ");
         Serial.println(pt100tChar);
      }
      dataString += ",";
      dataString += String(pt100tChar);
    } 

    SPIsettingsCOM();
    if(debug) Serial.println(dataString);
/*
    avg++;
    sumP += prsP;
    if (avg == 20) { avgP = sumP / (float)avg;  avg = 0; sumP = 0.0; }

    if      ((flightST == 0) && (prsP < 880.0)) { flightST = 1; }                   // going up
    else if ((flightST == 1) && (prsP > 920.0)) { flightST = 2; time =  millis(); } // going down 
    else if (flightST == 2) {                                                       // waiting for touch down
      dP = prsP - P0; P0 = prsP;
      if (dP < 0.5)  { checkcnt-- ; }                                                    // dP: pressure change per 3s
      else { checkcnt = 3; }
      dur = millis() - time ;                                                       // check time for fast ups and downs
      if ((dur > 180000)||(checkcnt <= 0)) {      flightST = 3; time = millis();
         analogWrite(AutoValve, 255); cutterON = 1;                                 // Burn ON
      }
    }
    else if (flightST == 3) {                                                       // Burner counting down.
      dur = millis() - time ;
      if (dur > 30000) {  flightST = 0;                                             // Finished.
        analogWrite(AutoValve, 0);
        cutterON = 0;
      }
    }
    if(debug) { Serial.print (flightST); Serial.print (" FLIGHT Mode "); Serial.println (cutterON); }
    dataString += ",";
    dataString += String(cutterON);
    dataString += ",";
    dataString += String(flightST);

   if(debug) { Serial.print (" Logging: "); Serial.println (charFileName); }
   if(debug) { Serial.print (" Data: ");    Serial.println (dataString); }
   if(debug) { Serial.print (" mode: ");    Serial.println (mode); }
   if(debug) { Serial.print (" Premode: "); Serial.println (previousMode); }
*/
delay(10000);

   File dataFile = SD.open(charFileName, FILE_WRITE);
   dataFile.println(dataString);
   dataFile.close();

}

