#include <SPI.h>
#include <SD.h>
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

const int airCore = 3; // Type airCore is used.
char sz[20];

const int SelectADC2 = 6;   // Temperature ADS1248 with 3x PT100
const int SelectADC1 = 7;   // Temperature ADS1248 with 3x PT100
const int SelectPRS  = 8;   // Pressure Sensor
const int SelectRTC  = 9;   // Real Time Clock
const int SelectSD   = 10;  // Micro SD card

void setup()
{
  findNewFileName(15, 15);

}

void findNewFileName(float t, float p)
{
  int type=3, month=06, day=01, year=15;
 // Open serial communications and wait for port to open:
  SPI.setClockDivider(SPI_CLOCK_DIV4);

  Serial.begin(9600);
   while (!Serial) {
    ; // wait for serial port to connect. Needed for Leonardo only
  }

  pinMode(SelectRTC, OUTPUT);
  pinMode(SelectPRS, OUTPUT);
  pinMode(SelectADC1, OUTPUT);
  pinMode(SelectADC2, OUTPUT);
  pinMode(SelectSD, OUTPUT);

  digitalWrite(SelectRTC, HIGH);
  digitalWrite(SelectPRS, HIGH);
  digitalWrite(SelectADC1, HIGH);
  digitalWrite(SelectADC2, HIGH);

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
  for (byte i=0; i < 100; i++)
  {
    sprintf(sz, "%02d%02d%02d%02d.csv", airCore, month, day, i);
    
    if (!SD.exists(sz))
    {
      break;
    }
  }
  if (debug) Serial.println(sz);
  
  myFile = SD.open(sz, FILE_WRITE);

  // if the file opened okay, write to it:
  if (myFile) {
    Serial.print("Writing to test.txt...");
    myFile.println("testing 1, 2, 3.");
    myFile.print(t);
    myFile.print(", ");
    myFile.print(p);
	// close the file:
    myFile.close();
    Serial.println("done.");
  } else {
    // if the file didn't open, print an error:
    Serial.print("error opening : ");
    Serial.println(sz);
  }
  
  // re-open the file for reading:
  myFile = SD.open(sz);
  if (myFile) {
    Serial.println(sz);
    
    // read from the file until there's nothing else in it:
    while (myFile.available()) {
    	Serial.write(myFile.read());
    }
    // close the file:
    myFile.close();
  } else {
  	// if the file didn't open, print an error:
    Serial.print("error opening : ");
    Serial.println(sz);
  }

}

void logThis(float pres,float temp)
{
  myFile = SD.open(sz, FILE_WRITE);

  // if the file opened okay, write to it:
  if (myFile) {
    Serial.print("Writing to test.txt...");
    myFile.print(pres);
    myFile.println(", ");
    myFile.close();
    Serial.println(pres);
    Serial.println("done.");
  } else {
    // if the file didn't open, print an error:
    myFile.close();
    delay(1000);
    Serial.print("error opening : ");
    Serial.println(sz);
    myFile = SD.open(sz, FILE_WRITE);

  // if the file opened okay, write to it:
    if (myFile) {
       Serial.print("Writing to test.txt...");
       myFile.println("testing 1, 2, 3.");
       myFile.print(pres);
       myFile.print(", ");
       myFile.print(temp);
	// close the file:
       myFile.close();
       Serial.println("done.");
     } else {
    // if the file didn't open, print an error:
       Serial.print("error opening : ");
       Serial.println(sz);
     }
  }
  
}



void loop()
{
  SPI.setClockDivider(SPI_CLOCK_DIV32);

  digitalWrite(SelectPRS,LOW);
  delay(10);
 
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
   
  byte stat0 = (inByte_1 >> 6) & 1;
  byte stat1 = (inByte_1 >> 7) & 1;
  Serial.print("STAT = ");Serial.print(stat0);Serial.print(" ");Serial.println(stat1);

  inByte_1 &= ~(1 << 6);
  inByte_1 &= ~(1 << 7);
  inByte_1 <<= 8;
  inByte_1 |= inByte_2;

  inByte_4 >>= 5;
//  inByte_3 <<= 3;
  inByte_3 |= inByte_4;

  float pressure = (((float)inByte_1 - 1638.0) * (15.0 - 0.0))/(14746.0 - 1638.0) + 0.0; 
  pressure *= 68.94757;
  Serial.print("pressure = ");Serial.println(pressure);
 
  float temperature = (float)inByte_3 * 200.0 / 2047.0 - 50.0; 
  Serial.print("temperature[C]= ");Serial.print(temperature);Serial.print("\n");
  
  digitalWrite(SelectPRS,HIGH);
  delay(500); 
  logThis(pressure, temperature);
  delay(500); 
  

}






