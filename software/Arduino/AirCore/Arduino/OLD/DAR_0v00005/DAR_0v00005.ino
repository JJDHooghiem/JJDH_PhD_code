/**********************************************************/
/************************** D A R *************************/ 
/**********************************************************/

// include the libraries
#include <SPI.h>            // used for SPI communication
#include <SD.h>             // used for SD card communication
#include <DS3234.h>         // used for Real Time Clock communication (IC:ds3234)
#include <SoftwareSerial.h> // used for serial communication
#include <TinyGPS.h>        // used for GPS data

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
const int SelectGPSR = 4;   // TX for GPS unit 
const int SelectGPST = 3;   // RX for GPS unit
const int AutoValve  = A3;  // Automatic valve, cutter for closing the coil.  

// constant and variables
volatile boolean mode;
boolean previousMode;
char    charFileName[13] = "yyyymmdd.xxx";
float   prsT, prsP;
byte    prsStat0, prsStat1, heaterON, cutterON, flightST;
char    prsPChar[10], prsTChar[10];
int     year, month, day, hour, minute, second;
int     wait = 10, burntime=7000;
unsigned long time = 0;

/* GPS code e normal use of a TinyGPS object.
   It requires the use of SoftwareSerial, and assumes that you have a
   9600-baud serial GPS device hooked up on pins 4(rx) and 3(tx).
*/

TinyGPS gps;
SoftwareSerial ss(SelectGPSR, SelectGPST);
/**********************************************/
boolean debug = true; // debug mode or real mode.
/**********************************************/

static void smartdelay(unsigned long ms);
static void print_float(float val, float invalid, int len, int prec);
static void print_int(unsigned long val, unsigned long invalid, int len);
static void print_date(TinyGPS &gps);
static void print_str(const char *str, int len);

void   SPIsettingsADC();
void   SPIsettingsADC();
void   SPIsettingsPRS();
void   setupADS1248(int CSPin);
float  readADS1248(int RTDId);
void   getPressure(float &pressure, float &temperature, byte &stat0, byte &stat1);
int    RTC_init();
int    SetTimeDate(int d, int mo, int y, int h, int mi, int s);
String serialReadString();
String ReadTimeDate();

void setup(void)
{
  Serial.begin(9600);
  ss.begin(9600);               // communication speed for GPS system.

  mode = false; 
  previousMode = !mode;
// Pin declaration  
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
  SD.begin(SelectSD);             // start SD card communication
  SPIsettingsADC();               // Set ADS1248 settings for SPI communication
  RTC_init();                     // initialize RTC    
  SetTimeDate(12,03,15,23,55,00); // day(1-31), month(1-12), year(0-99), hour(0-23), minute(0-59), second(0-59)
  setupADS1248(SelectADC1);       // SETUP ads1248
  setupADS1248(SelectADC2);       // 
  SPIsettingsCOM();               // Set COM settings for SPI communication   
}

void SPIsettingsADC()// setting for SPI communication with the ADS1248
{
  SPI.setDataMode(SPI_MODE1);
  delay(wait);
  SPI.setBitOrder(MSBFIRST);
  delay(wait);
  SPI.setClockDivider(SPI_CLOCK_DIV8);
  delay(wait);
}

void SPIsettingsCOM()// setting for SPI communication with the micro SD card
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
  digitalWrite(SelectPRS,LOW);
  delay(wait);
 
  int inByte_1 = SPI.transfer(0x00);
  int inByte_2 = SPI.transfer(0x00);
  int inByte_3 = SPI.transfer(0x00);
  int inByte_4 = SPI.transfer(0x00);
 
  Serial.print("Byte_1 = ");Serial.print(inByte_1,DEC);Serial.print(" ");
  Serial.print("Byte_2 = ");Serial.print(inByte_2,DEC);Serial.print(" ");
  Serial.print("Byte_3 = ");Serial.print(inByte_3,DEC);Serial.print(" ");
  Serial.print("Byte_4 = ");Serial.print(inByte_4,DEC);Serial.print(" ");
 
  float psi = inByte_1<<8|inByte_2;
  psi = (psi*5)/16384;
  Serial.print("PRES = ");Serial.print(psi);Serial.print(" ");
  inByte_3 = inByte_3<<3;
  float realTemp = ((float)inByte_3*200/2047)-50;
  Serial.print("Temp[C]= ");Serial.print(realTemp);Serial.print("\n");
   
  stat0 = (inByte_1 >> 6) & 1;
  stat1 = (inByte_1 >> 7) & 1;
  Serial.print("STAT = ");Serial.print(stat0);Serial.print(" ");Serial.println(stat1);

  inByte_1 &= ~(1 << 6);
  inByte_1 &= ~(1 << 7);
  inByte_1 <<= 8;
  inByte_1 |= inByte_2;

  inByte_4 >>= 5;
//  inByte_3 <<= 3;
  inByte_3 |= inByte_4;

  pressure = (((float)inByte_1 - 1638.0) * (15.0 - 0.0))/(14746.0 - 1638.0) + 0.0; 
  pressure *= 68.94757;
  Serial.print("pressure = ");Serial.println(pressure);
  temperature = (float)inByte_3 * 200.0 / 2047.0 - 50.0; 
  Serial.print("temperature[C]= ");Serial.print(temperature);Serial.print("\n");
  
  digitalWrite(SelectPRS,HIGH);
  delay(wait); 
}

int RTC_init(){ 
  digitalWrite(SelectRTC, LOW);  
  delay(wait);
  SPI.transfer(0x8E);
  SPI.transfer(0x60);           //60= disable Osciallator and Battery SQ wave @1hz, temp compensation, Alarms disabled
  digitalWrite(SelectRTC, HIGH);
  delay(wait);
}

int SetTimeDate(int d, int mo, int y, int h, int mi, int s){ 
  int TimeDate [7]={s,mi,h,0,d,mo,y};
  for(int i=0; i<=6;i++){
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

//=====================================
String ReadTimeDate(){
  String temp;
  int TimeDate [7]; //second,minute,hour,null,day,month,year		
  char sz[32];

  for(int i=0; i<=6;i++){
    if(i==3) i++;
    digitalWrite(SelectRTC, LOW);
    SPI.transfer(i+0x00); 
    unsigned int n = SPI.transfer(0x00);        
    digitalWrite(SelectRTC, HIGH);
    int a=n & B00001111;    
    if(i==2){	
      int b=(n & B00110000)>>4; //24 hour mode
      if(b==B00000010)      b=20;        
      else if(b==B00000001) b=10;
      TimeDate[i]=a+b;
    }
    else if(i==4){
      int b=(n & B00110000)>>4;
      TimeDate[i]=a+b*10;
    }
    else if(i==5){
      int b=(n & B00010000)>>4;
      TimeDate[i]=a+b*10;
    }
    else if(i==6){
      int b=(n & B11110000)>>4;
      TimeDate[i]=a+b*10;
    }
    else{	
      int b=(n & B01110000)>>4;
      TimeDate[i]=a+b*10;	
    }
  }
  day = TimeDate[4];    temp.concat(day);    temp.concat("/") ;
  month = TimeDate[5];  temp.concat(month);  temp.concat("/") ;
  year = TimeDate[6];   temp.concat(year);   temp.concat("     ") ;
  hour = TimeDate[2];   temp.concat(hour);   temp.concat(":") ;
  minute = TimeDate[1]; temp.concat(minute); temp.concat(":") ;
  second = TimeDate[0]; temp.concat(second);
  
  sprintf(sz, "%02d/%02d/%02d %02d:%02d:%02d ", month, day, year, hour, minute, second);
  Serial.println(sz);

  return(temp);
}

String serialReadString()// read a string from the serieel monitor
{ 
  char charIn;
  String stringOut;

  stringOut = "";

  while (!mode) {
    if (Serial.available() > 0) {
      charIn = Serial.read();
      if (charIn == '\n') { break; }
      else { stringOut += charIn;  }
    }
  }
  if(debug) Serial.println(stringOut);
  return stringOut;
}

//  function for the GPS data communication.

static void smartdelay(unsigned long ms)
{
  unsigned long start = millis();
  do { while (ss.available()) gps.encode(ss.read());
  } while (millis() - start < ms);
}

static void print_float(float val, float invalid, int len, int prec)
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

static void print_date(TinyGPS &gps)
{
  int year;
  byte month, day, hour, minute, second, hundredths;
  unsigned long age;
  gps.crack_datetime(&year, &month, &day, &hour, &minute, &second, &hundredths, &age);
  if (age == TinyGPS::GPS_INVALID_AGE) Serial.print("********** ******** ");
  else {
    char sz[32];
    sprintf(sz, "%02d/%02d/%02d %02d:%02d:%02d ", month, day, year, hour, minute, second);
    Serial.print(sz);
  }
  print_int(age, TinyGPS::GPS_INVALID_AGE, 5);
  smartdelay(0);
}

static void print_str(const char *str, int len)
{
  int slen = strlen(str);
  for (int i=0; i<len; ++i) Serial.print(i<slen ? str[i] : ' ');
  smartdelay(0);
}

void loop(void) 
{
  float pt100t;
  char  pt100tChar[10];
  String dataString, serialString;
  unsigned long dur;
  float flat, flon;
  unsigned long age, date, time, chars = 0;
  unsigned short sentences = 0, failed = 0;
  static const double LONDON_LAT = 51.508131, LONDON_LON = -0.128002;
  
  if (mode) // Working mode 
  {
    dataString = "";
    // Time reading 
    dataString += ReadTimeDate();
    // Pressure and temperatuur
    SPIsettingsPRS();
    getPressure(prsP, prsT, prsStat0, prsStat1);
    dtostrf(prsP, 1, 2, prsPChar);
    dtostrf(prsT, 1, 2, prsTChar);
    dataString += ",";  dataString += String(prsPChar);
    dataString += ",";  dataString += String(prsTChar);
    dataString += ",";  dataString += String(prsStat1);
    dataString += ",";  dataString += String(prsStat0);
     
    //Temperature reading 
    SPIsettingsADC(); 
    for (int i=1; i <= 6; i++){
      pt100t = readADS1248(i);
      dtostrf(pt100t, 1, 3, pt100tChar);
      Serial.print (i);
      Serial.print (" , ");
      Serial.println(pt100tChar);
      dataString += ",";
      dataString += String(pt100tChar);
    } 

    SPIsettingsCOM();
    Serial.println(dataString);

    if ((flightST == 0) && (prsP < 920.0))      { flightST = 1; }                   // going up
    else if ((flightST == 1) && (prsP > 880.0)) { flightST = 2; time =  millis(); } // going down 
    else if (flightST == 2) {                                                       // waiting for touch down
      dur = millis() - time ; // check time for fast ups and downs
      if (dur > 60/*0000*/) {
        flightST = 3;
        if(heaterON == 1){
          analogWrite(AutoValve, 0);
          heaterON = 0;
        }
        analogWrite(AutoValve, 255);
        heaterON = 1;
        time = millis();
      }
    }
    else if (flightST == 3) {
      dur = millis() - time ;
      if (dur > 30000) {
        flightST = 0;
        analogWrite(AutoValve, 0);
        heaterON = 0;
      }
    }
    Serial.print (flightST); Serial.print (" FLIGHT Mode "); Serial.println (cutterON);
    dataString += ",";
    dataString += String(cutterON);
    dataString += ",";
    dataString += String(flightST);

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
      Serial.println("!TIME ?TIME OPEN_VALVE GPS_CHECK QUIT");
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
        Serial.println("Set Year (yy): ");
        year = serialReadString().toInt();
        Serial.println("Set Month (mm): ");
        month = serialReadString().toInt();
        Serial.println("Set day (dd): ");
        day = serialReadString().toInt();
        Serial.println("Set hour (HH): ");
        hour = serialReadString().toInt();
        Serial.println("Set minute (MM): ");
        minute = serialReadString().toInt();
        Serial.println("Set seconde (SS):");
        second = serialReadString().toInt();
        if (!mode)
        {
          Serial.print("Time set to: ");
          SetTimeDate(day,month,year,hour,minute,second); //day(1-31), month(1-12), year(0-99), hour(0-23), minute(0-59), second(0-59)
          Serial.println(ReadTimeDate());
          Serial.println("Give a command:");
        }
      }
      else if (serialString == "OPEN_VALVE")
      {
        Serial.println("Opening the valve ...");
        if (!mode)
        {
          analogWrite(AutoValve, 255);
          delay(burntime);
          analogWrite(AutoValve, 0);
          Serial.println("Ready");
          Serial.println("Give a command:");
        }
      }
      else if (serialString == "GPS_CHECK")
      {
        Serial.println("Check the GPS unit ...");
        if (!mode)
        {
          Serial.println("Sats HDOP Latitude ");
          gps.f_get_position(&flat, &flon, &age);
//          print_float(flat, TinyGPS::GPS_INVALID_F_ANGLE, 10, 6);
 //         print_float(flon, TinyGPS::GPS_INVALID_F_ANGLE, 11, 6);

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





