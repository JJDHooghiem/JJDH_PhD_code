/*
  SD card read/write
 
 This example shows how to read and write data to and from an SD card file 	
 The circuit:
 * SD card attached to SPI bus as follows:
0 ** MOSI - pin 11
 ** MISO - pin 12
 ** CLK - pin 13
 ** CS - pin 4
 
 created   Nov 2010
 by David A. Mellis
 modified 9 Apr 2012
 by Tom Igoe
 
 This example code is in the public domain.
 	 
 */
 
#include <SD.h>

File myFile;
/**********************************************/
boolean debug = true; // debug mode or real mode.
/**********************************************/

const int airCore = 9; // Type airCore is used.
char sz[20];

const int SelectSD      = 10;  // Micro SD card
const int SelectRTC     = 9;   // Real Time Clock
const int SelectPRS     = 8;   // Pressure Sensor
const int SelectPRS2    = 43;
const int SelectADC1    = 7;   // Temperature ADS1248 with 3x PT100
const int SelectADC2    = 6;   // Temperature ADS1248 with 3x PT100const int SelectADC2 = 6;   // Temperature ADS1248 with 3x PT100

int month=04, day=01, year=17;

void setup()
{
  findNewFileName(); 
}

void findNewFileName()
{

 // Open serial communications and wait for port to open:
  Serial.begin(9600);
   while (!Serial) {
    ; // wait for serial port to connect. Needed for Leonardo only
  }

  pinMode(SelectSD, OUTPUT);
  pinMode(SelectRTC, OUTPUT);
  pinMode(SelectPRS, OUTPUT);
  pinMode(SelectPRS2, OUTPUT);
  pinMode(SelectADC1, OUTPUT);
  pinMode(SelectADC2, OUTPUT);

  digitalWrite(SelectSD, HIGH);
  digitalWrite(SelectRTC, HIGH);
  digitalWrite(SelectPRS, HIGH);
  digitalWrite(SelectPRS2, HIGH);
  digitalWrite(SelectADC1, HIGH);
  digitalWrite(SelectADC2, HIGH);
  delay(100);
  digitalWrite(SelectSD, LOW);

  Serial.print("Initializing SD card...");
  // On the Ethernet Shield, CS is pin 4. It's set as an output by default.
  // Note that even if it's not used as the CS pin, the hardware SS pin 
  // (10 on most Arduino boards, 53 on the Mega) must be left as an output 
  // or the SD library functions will not work. 
  delay(10);   
  if (!SD.begin(SelectSD)) {
    Serial.println("initialization failed!");
    Serial.println("Check SD!");
    return;
  }
  Serial.println("initialization done.");
  
  // open the file. note that only one file can be open at a time,
  // so you have to close this one before opening another.
  for (byte i=0; i < 100; i++)
  {
    sprintf(sz, "%02d%02d%02d%02d.csv", airCore, month, day, i);
    
    if (!SD.exists(sz))
    {
      break;
    }
  }
  if (debug) Serial.println(sz);

  Serial.print("Writing to ");
  
  myFile = SD.open(sz, FILE_WRITE);

  // if the file opened okay, write to it:
  if (myFile) {
    Serial.println(sz);
    delay(10);
    myFile.println("testing 1, 2, 3.");
	// close the file:
    Serial.print("closing the file...");
    myFile.close();
    Serial.println("done.");
  } else {
    // if the file didn't open, print an error:
    Serial.print("error opening : ");
    Serial.println(sz);
  }
  
  // re-open the file for reading:
  Serial.print("Re-Opening the file...");
  Serial.println(sz);
  delay(100);
  myFile = SD.open(sz);
  delay(10);
  if (myFile) {
    Serial.println(sz);
    // read from the file until there's nothing else in it:
    while (myFile.available()) { Serial.write(myFile.read()); }
    // close the file:
    Serial.println("closing the file...");
    delay(100);
    myFile.close();
    Serial.println("done.");
  } else {
  	// if the file didn't open, print an error:
    Serial.print("error opening : ");
    Serial.println(sz);
  }

}

void loop()
{
  // nothing happens after setup

}


