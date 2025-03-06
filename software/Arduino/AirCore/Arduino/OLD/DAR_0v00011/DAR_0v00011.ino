/**********************************************************/
/************************** D A R *************************/ 
/**********************************************************/

// include the libraries
#include <SD.h>       // used for SD card communication
#include <SPI.h>      // used for SPI communication
#include <DS3234.h>   // used for Real Time Clock communication (IC:ds3234)

#define LOGFILE "datalog1.txt"
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

void setup()
{
  Serial.begin(9600);
  Serial.println("**** SETTING ****");
  Serial.println(LOGFILE);


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

  findNewFileName();

}

void findNewFileName()
{
 // Open serial communications and wait for port to open:
  SPI.setClockDivider(SPI_CLOCK_DIV4);
  Serial.print("Initializing SD card...");
  // On the Ethernet Shield, CS is pin 4. It's set as an output by default.
  // Note that even if it's not used as the CS pin, the hardware SS pin 
  // (10 on most Arduino boards, 53 on the Mega) must be left as an output 
  // or the SD library functions will not work. 
   
  if (!SD.begin(SelectSD)) {
    Serial.println("initialization failed!");
    return;
  }
  Serial.println("initialization done.");
  
  // open the file. note that only one file can be open at a time,
  // so you have to close this one before opening another.
  if (debug) Serial.println(LOGFILE);
  
  myFile = SD.open(LOGFILE, FILE_WRITE);

  // if the file opened okay, write to it:
  if (myFile) {
    Serial.print("Writing to test.txt...");
    myFile.println("testing 1, 2, 3.");
    myFile.print(", 15-06-17 ");
    	// close the file:
    myFile.close();
    Serial.println("done.");
  } else {
    // if the file didn't open, print an error:
    Serial.print("error opening : ");
    Serial.println(LOGFILE);
  }
  
  // re-open the file for reading:
  myFile = SD.open(LOGFILE);
  if (myFile) {
    Serial.println(LOGFILE);
    
    // read from the file until there's nothing else in it:
    while (myFile.available()) {
    	Serial.write(myFile.read());
    }
    // close the file:
    myFile.close();
  } else {
  	// if the file didn't open, print an error:
    Serial.print("error opening : ");
    Serial.println(LOGFILE);
  }

}

void logThis(double p, double t)
{
  
  myFile = SD.open(LOGFILE, FILE_WRITE);

  // if the file opened okay, write to it:
  if (myFile) {
    Serial.print("Writing logThis...");
    Serial.print(t);
    myFile.print(p);
    myFile.print(", ");
    myFile.print(t);
    myFile.print(", ");
    myFile.close();
    Serial.println("done.");
  } else {
    // if the file didn't open, print an error:
    myFile.close();
    delay(1000);
    Serial.print("error opening : ");
    Serial.println(LOGFILE);
  }
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



void loop()
{
  char msg[25];

    dataString = "";
    // Time reading 

//    dataString += ReadTimeDate();
    // Pressure and temperatuur
    getPressure(prsP, prsT, prsStat0, prsStat1);
    dtostrf(prsP, 1, 2, prsPChar);
    dtostrf(prsT, 1, 2, prsTChar);
    dataString += ",";  dataString += String(prsPChar);
    dataString += ",";  dataString += String(prsTChar);
    dataString += ",";  dataString += String(prsStat1);
    dataString += ",";  dataString += String(prsStat0);

 
  Serial.print("pressure = ");Serial.println(pressure);
 
  double temperature = (double)inByte_3 * 200.0 / 2047.0 - 50.0; 
  Serial.print("temperature[C]= ");Serial.print(temperature);Serial.print("\n");
  
  digitalWrite(SelectPRS,HIGH);

  delay(500); 

  
  Serial.print("Message= ");
  Serial.print("pressure= ");
  Serial.print(pressure);
  Serial.print("temperature= ");
  Serial.println(temperature);
  
  delay(5000); 
  logThis(pressure,temperature);
  delay(500); 
  

}






