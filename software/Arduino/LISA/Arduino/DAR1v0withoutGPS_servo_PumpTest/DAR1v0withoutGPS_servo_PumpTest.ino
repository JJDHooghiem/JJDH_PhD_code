/**********************************************************/
/************************** D A R *************************/ 
/**********************************************************/

// include the libraries
//#include <SoftwareSerial.h>
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

/*static void smartdelay(unsigned long ms);
static float print_float(float val, float invalid, int len, int prec);
static void print_int(unsigned long val, unsigned long invalid, int len);
static String print_date(TinyGPS &gps);
static void print_str(const char *str, int len);
*/

/**********************************************/
boolean debug = false; // debug mode or real mode.
/**********************************************/

Servo OutServo;   // create servo object to control a servo of Output 
Servo PackServo;  // create servo object to control a servo of Pack´s
 
const int airCore = 9; // Type airCore/Package is used.

// constant and variables
volatile boolean mode;
boolean previousMode; 
 
int pumpON = 0, delayPump = 30, Pmax = 300, SelectServo;
int P1=200 , P2=120, P3=80, P4=30;
byte year, month, date;

char charFileName[13]; 
//int TimeDate[7] = {0,0,0,0,0,0,0}; //second,minute,hour,null,day,month,year
unsigned long time = 0;

// pin description of the Adruino Mega

const int SelectSD   = 49;   // Micro SD card
const int SelectRTC  = 47;   // Real Time Clock
const int SelectPRS  = 48;   // Pressure Sensor
const int SelectPRS1 = 43;   // Pressure Sensor
const int SelectADC1 = 46;   // Temperature ADS1248 with 3x PT100
const int SelectADC2 = 45;   // Temperature ADS1248 with 3x PT100

const int SelectPack0 = 2;  // Valve Pack unit 0
const int SelectPack1 = 3;  // Valve Pack unit 1 A
const int SelectPack2 = 4;  // Valve Pack unit 2
const int SelectPack3 = 5;  // Valve Pack unit 3 
const int SelectPack4 = 6;  // Valve Pack unit 3 

const int SelectPump = 12;   // Pump unit
const int SelectLED  = 13;   // Pump unit

int Pack1 = 0,Pack2 = 0, Pack3 = 0, Pack4 = 0; 
int OpenPack = 180, ClosePack = 0, PosistionPack; //MIN 0  MAX 180


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
  pinMode(SelectADC2, OUTPUT);
  pinMode(SelectPack0, OUTPUT);
  pinMode(SelectPack1, OUTPUT);
  pinMode(SelectPack2, OUTPUT);
  pinMode(SelectPack3, OUTPUT);
  pinMode(SelectPack4, OUTPUT);
  pinMode(SelectPump, OUTPUT);
  pinMode(SelectLED, OUTPUT);

  digitalWrite(SelectSD,   HIGH);
  digitalWrite(SelectPRS,  HIGH);
  digitalWrite(SelectPRS1,  HIGH);
  digitalWrite(SelectRTC,  HIGH);
  digitalWrite(SelectADC2, HIGH);
  digitalWrite(SelectPack0, HIGH);
  digitalWrite(SelectPack1, HIGH);
  digitalWrite(SelectPack2, HIGH);
  digitalWrite(SelectPack3, HIGH);
  digitalWrite(SelectPack4, HIGH);
  digitalWrite(SelectPump, LOW);
  digitalWrite(SelectLED, LOW);
 
  SPI.begin();
  SD.begin(SelectSD);
  Setup_RTC();
  SPIsettingsADC();
  setupADS1248(SelectADC1);
  setupADS1248(SelectADC2);
  
}

// Used for the Clock(RTC) 
void SPIsettingsCOM()
{
  SPI.setDataMode(SPI_MODE1);
  delay(10);
  SPI.setBitOrder(MSBFIRST);
  delay(10);
  SPI.setClockDivider(SPI_CLOCK_DIV4);
  delay(10);
}

// Used for the ADS1248 Temperature sensors 
void SPIsettingsADC()  
{
  if(debug) Serial.print("setting ADS1248.... ");
  SPI.setDataMode(SPI_MODE1);
  delay(10);
  if(debug) Serial.print("SPI_MODE1.... ");
  SPI.setBitOrder(MSBFIRST);
  delay(10);
  if(debug) Serial.print("MSBFIRST.... ");
  SPI.setClockDivider(SPI_CLOCK_DIV8);
  delay(10);
  if(debug) Serial.print("SPI_CLOCK_DIV8.... ");
  if(debug) Serial.println(" done! ");
}

/*** Temperature sensor  ***/
void setupADS1248(int CSPin)
{ /* setup for the temperature sensors, ref. doc. ADS1248 */
  if(debug) Serial.print("setup ADS1248.... ");
  digitalWrite(CSPin, LOW);
  delay(10);

  if(debug) Serial.print(CSPin);

  SPI.transfer(0x06);        // RESET IC 
  delay(250);                // Min. 0.6 ms

  if(debug) Serial.print(" reset,.. ");

  SPI.transfer(0x16);        // Stop reading continuosly
  delay(10);
  
  if(debug) Serial.print(" stop reading,.. ");
  
  SPI.transfer(0x43);        // Write to SYS0
  SPI.transfer(0x00);
  SPI.transfer(0x44);        // PGA 16x, 80SPS
  delay(250);

  if(debug) Serial.print(" write SYS0,.. ");  

  SPI.transfer(0x42);        // Write to MUX1
  SPI.transfer(0x00);
  SPI.transfer(0x28);        // Int. oscl. ON, int. ref. ON, REF1, normal oper.
  delay(250);

  if(debug) Serial.print(" write MUX1,.. ");
    
  SPI.transfer(0x4A);        // Write to IDAC0
  SPI.transfer(0x00);
  SPI.transfer(0x06);        // DRDY OFF, I1&I2 1mA
  delay(250);

  if(debug) Serial.print(" write IDAC0,.. ");
  
  digitalWrite(CSPin, HIGH);
  delay(10);
  if(debug)   Serial.println(" done. ");
}

float readADS1248(int RTDId) 
{ 
  unsigned long outADC = 0;
  byte byteMSB, byteMID, byteLSB;
  float degC;

  digitalWrite(SelectADC2, LOW);
  delay(50);
  if(debug) Serial.println("slaveSelectPin,LOW ");

  // Write to IDAC1
  if (RTDId == 1) {      SPI.transfer(0x4B); SPI.transfer(0x00); SPI.transfer(0x8C); }// I1 to IEXT1, I2 OFF
  else if (RTDId == 2) { SPI.transfer(0x4B); SPI.transfer(0x00); SPI.transfer(0x2C); }// I1 to AIN2, I2 OFF
  else if (RTDId == 3) { SPI.transfer(0x4B); SPI.transfer(0x00); SPI.transfer(0x3C); }// I1 to AIN3, I2 OFF
  delay(50);
  
  // Write to MUX0
  if (RTDId == 1) {      SPI.transfer(0x40); SPI.transfer(0x00); SPI.transfer(0x01); }// Burnout OFF, AIN0 +IN, AIN1 -IN
  else if (RTDId == 2) { SPI.transfer(0x40); SPI.transfer(0x00); SPI.transfer(0x25); }// Burnout OFF, AIN4 +IN, AIN5 -IN
  else if (RTDId == 3) { SPI.transfer(0x40); SPI.transfer(0x00); SPI.transfer(0x37); }// Burnout OFF, AIN6 +IN, AIN7 -IN
  delay(50);
  
  SPI.transfer(0x12); // Read data once
  byteMSB = SPI.transfer(0xFF); // MSB
  if(debug) Serial.print("byteMSB ");
  if(debug) Serial.print(byteMSB);
  byteMID = SPI.transfer(0xFF); // Mid-Byte
  if(debug) Serial.print("byteMID ");
  if(debug) Serial.print(byteMID);
  byteLSB = SPI.transfer(0xFF); // LSB
  if(debug) Serial.print("byteLSB ");
  if(debug) Serial.println(byteLSB);
  outADC |= byteMSB;
  outADC <<= 8;
  outADC |= byteMID;
  outADC <<= 8;
  outADC |= byteLSB;
  if(debug) {
    Serial.print("byteMSB "); Serial.println(byteMSB);
    Serial.print("byteMID "); Serial.println(byteMID);
    Serial.print("byteLSB "); Serial.println(byteLSB);
  }
  degC = (2.4 / 16.0) / (pow(2.0, 23.0) - 1.0) * float(outADC); // Voltage
  degC /= 1.0e-3;                                               // Resistance
  degC = (degC - 100.0) / (3850e-6 * 100.0);                    // Temperature

  digitalWrite(SelectADC2, HIGH);

  return degC;
}
/*** End of Temperature sensor  ***/

/***  Clock reading ***/

int Setup_RTC(){ 
  if(debug) Serial.print("setting RTClock.... ");
   
  SPI.setBitOrder(MSBFIRST); 
  SPI.setDataMode(SPI_MODE1); // both mode 1 & 3 should work 
  //set control register 
  digitalWrite(SelectRTC, LOW);
  delay(10);  
  SPI.transfer(0x8E);
  SPI.transfer(0x60); //60= disable Osciallator and Battery SQ wave @1hz, temp compensation, Alarms disabled
  digitalWrite(SelectRTC, HIGH);
  if(debug) Serial.println("RTClock setup done. ");

}

int SetTimeDate(int d, int mo, int y, int h, int mi, int s){ 
  int TimeDate [7]={s,mi,h,0,d,mo,y};
  for(int i=0; i<=6;i++){
    if(i==3)
      i++;
    int b= TimeDate[i]/10;
    int a= TimeDate[i]-b*10;
    if(i==2){
      if (b==2)
        b=B00000010;
      else if (b==1)
        b=B00000001;
    } 
    TimeDate[i]= a+(b<<4);
      
    digitalWrite(SelectRTC, LOW);
    delay(10);
    SPI.transfer(i+0x80); 
    SPI.transfer(TimeDate[i]);        
    digitalWrite(SelectRTC, HIGH);
  }
}

String ReadTimeDate() {
  String temp; 
  int b, i, TimeDate[7] = {0,0,0,0,0,0,0};
  char szd[32];
  
  for(i=0; i<=6;i++){
    if(i==3) i++;
    
    digitalWrite(SelectRTC, LOW);
    delay(10);
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

  sprintf(szd, "%02d/%02d/%02d %02d:%02d:%02d ", TimeDate[6], TimeDate[5], TimeDate[4], TimeDate[2], TimeDate[1], TimeDate[0]);
  if(debug)   Serial.println(szd);
  return(szd);
}


void timeByte(String datiStr, byte &year, byte &month, byte &date, byte &hour, byte &minute, byte &sec)
{  // reading the time.  
  year   = byte(datiStr.substring(2,4).toInt());
  month  = byte(datiStr.substring(5,7).toInt());
  date   = byte(datiStr.substring(8,10).toInt());
  hour   = byte(datiStr.substring(11,13).toInt());
  minute = byte(datiStr.substring(14,16).toInt());
  sec    = byte(datiStr.substring(17).toInt());
}


/*** End of Clock reading ***/

/*** Pressure sensor ***/ 

void getPressure(float &pressure, float &temperature, int prs)
{
  int byte1, byte2, byte3, byte4, CSPin;

  if (prs == 0) {  CSPin = SelectPRS; }
  else { CSPin = SelectPRS1; }
  
  SPI.setClockDivider(SPI_CLOCK_DIV32);
  digitalWrite(CSPin, LOW);
  delay(10);
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
  if(debug) {  Serial.print("pressure = ");Serial.println(pressure); }
 
  temperature = (float)byte3 * 200.0 / 2047.0 - 50.0; 
  if(debug) {  Serial.print("temperature[C]= ");
    Serial.println(temperature);
    Serial.print("\n");
  }
}

/*** End of Pressure sensor ***/

/*** New File ***/

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

/*** End of new File ***/ 

/*** Select modes ***/

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

/*** End of select modes ***/

/*** Servo's ***/

void Setup_Servo()
{
  OutServo.attach(SelectPack0);      // attaches the servo on pin 9 to the servo object 
  delay(500);
  
  Serial.print(" Output was : ");
  Serial.println(OutServo.read());
  OutServo.write(ClosePack);    // sets the servo position according to the scaled value 
  delay(500);

  OutServo.write(OpenPack);    // sets the servo position according to the scaled value 
  delay(800);
  Serial.print(" Output is set : ");
  Serial.println(OutServo.read());
  delay(500);
  OutServo.detach();               // attaches the servo on pin 9 to the servo object 
  for(int SelectServo=3; SelectServo<=6; SelectServo++)
  {
    PackServo.attach(SelectServo);       // attaches the servo on pin  to the servo object 
    delay(500);
    PackServo.write(OpenPack);    // sets the servo position according to the scaled value 
    delay(800);
    Serial.print(SelectServo);
    Serial.print(" Pack was : ");
    Serial.println(PackServo.read());
  
    PackServo.write(ClosePack);    // sets the servo position according to the scaled value 
    delay(800);
    
    Serial.print(SelectServo);
    Serial.print(" is set : ");
    Serial.println(PackServo.read());
    delay(500);
    PackServo.detach();               // attaches the servo on pin  to the servo object 
  }  

  Serial.println(" Connect packages NOW!!! ");
}

void setServo()
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

/*** End of Servo's ***/

/*** GPS unit ***/

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
    if(debug) Serial.print(sz);
  }
  print_int(age, TinyGPS::GPS_INVALID_AGE, 5);
  smartdelay(0);

  return(sz);

}

static void print_int(unsigned long val, unsigned long invalid, int len)
{
  char sz[32];
  if (val == invalid) strcpy(sz, "*******");
  else sprintf(sz, "%ld", val);
  sz[len] = 0;
  for (int i=strlen(sz); i<len; ++i) sz[i] = ' ';
  if (len > 0) sz[len-1] = ' ';
  if(debug) Serial.print(sz);
  smartdelay(0);
}

static float print_float(float val, float invalid, int len, int prec)
{
  if (val == invalid) { while (len-- > 1) Serial.print('*'); Serial.print(' '); }
  else {
    if(debug) Serial.print(val, prec);
    int vi = abs((int)val);
    int flen = prec + (val < 0.0 ? 2 : 1); // . and -
    flen += vi >= 1000 ? 4 : vi >= 100 ? 3 : vi >= 10 ? 2 : 1;
    for (int i=flen; i<len; ++i) Serial.print(' ');
  }
  smartdelay(0);
  return val;
}

static void smartdelay(unsigned long ms)
{
  unsigned long start = millis();
  do { while (Serial1.available()) gps.encode(Serial1.read());
  } while (millis() - start < ms);
}

/*** End of GPS unit ***/


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

  digitalWrite(SelectLED, HIGH);
  if (mode) {
    if (mode != previousMode) {
      Serial.println("... working in cosmacmode");
      findNewFileName();
      Serial.print("Writing to ");
      Serial.println(charFileName);
      previousMode = mode;
      File dataFile = SD.open(charFileName, FILE_WRITE);
//      dataFile.println("GPS Date, Latitude, Longitude, altitude, Date, PressureOut, TemperatureOut, PressureIn, TemperatureIn, T0, T1, T2, P1, P2, P3, P4, Pmax, Pump_delay, Pump_time, Pack1, Pack2, Pack3, Pack4");
      dataFile.println("Date, PressureOut, TemperatureOut, PressureIn, TemperatureIn, T0, T1, T2, P1, P2, P3, P4, Pmax, Pump_delay, Pump_time, Pack1, Pack2, Pack3, Pack4");
      dataFile.close();
    }

    dataString = "";

/* GPS * /
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
    dataString += String(faltChar);
    dataString += ",";
    smartdelay(1000);

/ *   END GPS */

    SPIsettingsCOM();
    dataString += ReadTimeDate(); // read time
  
    getPressure(prsP, prsT, 0);   // read pressure with the temperature 
   
    dtostrf(prsP, 1, 2, prsPChar);
    dtostrf(prsT, 1, 2, TChar);

    dataString += ",";
    dataString += String(prsPChar);
    dataString += ",";
    dataString += String(TChar);

    getPressure(prsP1, prsT, 1); // read pressure with the temperature 
   
       
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
      if(debug) { 
        Serial.print (i);
        Serial.print (" , ");
        Serial.println(TChar);
      }
    }
    if(debug) Serial.print("pumpON : "); // display tekst to scherm. 
    if(debug) Serial.print(pumpON);      // display tekst to scherm. 
    if(debug) Serial.print("prsP : ");   // display tekst to scherm. 
    if(debug) Serial.println(prsP);      // display tekst to scherm. 

    if(pumpON > 1) { pumpON -=1; }
    
    if ((prsP <= P1)&&(Pack1 == 0)) 
    {
      Serial.println("    Pack1"); // display tekst to scherm. 
      SelectServo = SelectPack1;
      Pack1 = 1;
      pumpON = delayPump;
    }
    else if ((prsP <= P2)&&(Pack2 == 0)) 
    {
      Serial.println("    Pack2"); // display tekst to scherm. 
      SelectServo = SelectPack2;
      Pack2 = 1;
      pumpON = delayPump;
    }  
    else if ((prsP <= P3)&&(Pack3 == 0)) 
    {
      Serial.println("     Pack3"); // display tekst to scherm. 
      SelectServo = SelectPack3;
      Pack3 = 1;
      pumpON = delayPump;
    }  
    else if ((prsP <= P4)&&(Pack4 == 0)) 
    {
      Serial.println("     Pack4"); // display tekst to scherm. 
      SelectServo = SelectPack4;
      Pack4 = 1;
      pumpON = delayPump;
    }  
    digitalWrite(SelectLED, LOW);


/* ******* Check Pressure inside ********************* */
    if ((prsP1 >= Pmax)&&(pumpON > 7)) 
    { // check inside pressure, when measurement is running 
      Serial.print(" Pressure actived : "); // display tekst to scherm. 
      Serial.print(prsP1); // display tekst to scherm. 
      Serial.print(" Pmax : "); // display tekst to scherm. 
      Serial.println(Pmax); // display tekst to scherm. 
      pumpON = 6;
    }  
    else { }

/* ******* Measssurement Package ********************* */
    delay(50);      

    if (pumpON == delayPump) 
    { //start-up
      OutServo.attach(SelectPack0);        // attaches the servo on pin 9 to the servo object 
      PackServo.attach(SelectServo);       // attaches the servo on pin 9 to the servo object 
      Serial.print("pumpON == delayPump attach servo             "); // display tekst to scherm. 
      Serial.println(SelectServo); // display tekst to scherm. 
    }
    else if (pumpON == (delayPump-1))  
    { // start pump
      OutServo.write(OpenPack);           // sets the servo position according to the scaled value 
      PackServo.write(ClosePack);           // sets the servo position according to the scaled value 
      Serial.print("pumpON == (delayPump-1) Open/close servo    <<***>>         "); // display tekst to scherm. 
      Serial.println(SelectServo); // display tekst to scherm. 
    }
    else if (pumpON == (delayPump-2))  
    { // start pump
      OutServo.detach();                // attaches the servo on pin 9 to the servo object 
      PackServo.detach();               // attaches the servo on pin 9 to the servo object   
  
      digitalWrite(SelectPump, HIGH);
      
      Serial.println("pumpON == (delayPump-2) detach Servo and Start Pumpy"); // display tekst to scherm. 
    }  
    delay(500);      

    if (pumpON == (delayPump-11)) 
    { //start-up
      OutServo.attach(SelectPack0);        // attaches the servo on pin 9 to the servo object 
      PackServo.attach(SelectServo);       // attaches the servo on pin 9 to the servo object 
      Serial.print("pumpON == (delayPump-11)  attach servo          "); // display tekst to scherm. 
      Serial.println(SelectServo); // display tekst to scherm. 
    }
    else if (pumpON == (delayPump-12)) 
    { // servo package open
      PackServo.write(OpenPack);           // sets the servo position according to the scaled value 
      OutServo.write(ClosePack);           // sets the servo position according to the scaled value 
      Serial.println("pumpON == (delayPump-12)  Open Package <<**>> "); // display tekst to scherm. 
    }  
    else if (pumpON == (delayPump-13)) 
    { // servo package open
      OutServo.detach();                // attaches the servo on pin 9 to the servo object 
      PackServo.detach();               // attaches the servo on pin 9 to the servo object   
      Serial.println("pumpON == (delayPump-13) detach servo <<**>> "); // display tekst to scherm. 
    }  

/* ***************************************** */    

    else if (pumpON == 6) 
    {
      PackServo.attach(SelectServo);       // attaches the servo on pin 9 to the servo object 
      Serial.println("pumpON == 6 attach servo <<**>> "); // display tekst to scherm. 
    }  
    else if (pumpON == 5) 
    {
      PackServo.write(ClosePack);        // sets the servo position according to the scaled value
      Serial.println("pumpON == 5 close Package <<**>> "); // display tekst to scherm. 
    }  
    else if (pumpON == 4) 
    {
      digitalWrite(SelectPump, LOW);
      PackServo.detach();               // attaches the servo on pin 9 to the servo object   
      Serial.println("pumpON == 4 detach servo  "); // display tekst to scherm. 
      OutServo.attach(SelectPack0);      // attaches the servo on pin 9 to the servo object 
      Serial.println("attach output  "); // display tekst to scherm. 
    }  
    else if (pumpON == 3) 
    {
      OutServo.write(OpenPack);          // sets the servo position according to the scaled value 
      Serial.println("pumpON == 3 open output  <<**>> "); // display tekst to scherm. 
    }  
    else if (pumpON == 2) 
    {
      OutServo.detach();                // attaches the servo on pin 9 to the servo object 
      Serial.println("pumpON == 2 detach Output <<**>> "); // display tekst to scherm. 
    }  
    else { }
    
    dataString += ","; dataString += String(P1);
    dataString += ","; dataString += String(P2);
    dataString += ","; dataString += String(P3);
    dataString += ","; dataString += String(P4);
    dataString += ","; dataString += String(Pmax);
    dataString += ","; dataString += String(SelectServo);    
    dataString += ","; dataString += String(delayPump);
    dataString += ","; dataString += String(pumpON);
    dataString += ","; dataString += String(Pack1);
    dataString += ","; dataString += String(Pack2);
    dataString += ","; dataString += String(Pack3);
    dataString += ","; dataString += String(Pack4);
  
    Serial.println(dataString);
  
    digitalWrite(SelectLED, LOW);
 
    File dataFile = SD.open(charFileName, FILE_WRITE);
    dataFile.println(dataString);
    dataFile.close();
    /***********************/
           Serial.println("Pulse high");
           digitalWrite(SelectPump, HIGH);   // turn the LED on (HIGH is the voltage level)
           delay(5000);                       // wait for a second
           Serial.println("Pulse low.");
           digitalWrite(SelectPump, LOW);    // turn the LED off by making the voltage LOW

    /***********************/

           Setup_Servo();

    /***********************/

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
        SPIsettingsCOM();
        Serial.println("Set time (yyyy-mm-dd HH:MM:SS):");
        serialString = serialReadString();
        if (!mode)
        {
          timeByte(serialString, year, month, date, hour, minute, sec);
      //  SetTimeDate(int d, int mo, int y, int h, int mi, int s)
          SetTimeDate(date, month, year, hour, minute, sec);
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
           Pmax = serialString.toInt();
           Serial.print("Pressure set to: ");
           Serial.println(Pmax);
           setServo();

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
           Pmax = serialString.toInt();
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
           P1 = serialString.toInt();
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
           P2 = serialString.toInt();
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
      else if (serialString == "SERVO")
      {
        Serial.println("Servo  ...");
        if (!mode)
        {
           String serialString; 
           Serial.println("Set servo to orginal place.");
           Setup_Servo();
           Serial.println("Give a command:");
        }
      }
      else if (serialString == "PULSE")
      {
        Serial.println("Pulse  ...");
        if (!mode)
        {
           Serial.println("Pulse high");
           digitalWrite(SelectPump, HIGH);   // turn the LED on (HIGH is the voltage level)
           delay(20000);                       // wait for a second
           Serial.println("Pulse low.");
           digitalWrite(SelectPump, LOW);    // turn the LED off by making the voltage LOW
           delay(20000);                       // wait for a second
           digitalWrite(SelectPump, HIGH);   // turn the LED on (HIGH is the voltage level)
           Serial.println("Pulse high");
           delay(20000);                       // wait for a second
           digitalWrite(SelectPump, LOW);    // turn the LED off by making the voltage LOW
           delay(20000);                       // wait for a second
           Serial.println("Pulse low");
           Serial.println("Give a command:");
        }
      }
        
      else if (serialString == "GPS")
      {
        Serial.print("GPS reading ...:");
        if (!mode)
        {
          for (int i=0; i <= 15; i++)
          {
            Serial.print(print_date(gps));
            Serial.print(", ");
            gps.f_get_position(&flat, &flon, &age);
            dtostrf(flat, 4, 6, flatChar);
            Serial.print(String(flatChar));
            Serial.print(", ");
            dtostrf(flon, 4, 6, flonChar);
            Serial.print(String(flonChar));
            Serial.print(", ");
            falt = print_float(gps.f_altitude(), TinyGPS::GPS_INVALID_F_ALTITUDE, 7, 2);
            dtostrf(falt, 4, 6, faltChar);
            Serial.print(String(faltChar));
            Serial.print(", ");
            Serial.print(String(print_float(gps.f_altitude(), TinyGPS::GPS_INVALID_F_ALTITUDE, 7, 2)));
            Serial.println(". ");
            smartdelay(1000);
          }
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

