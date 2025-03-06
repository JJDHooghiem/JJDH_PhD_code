#include <SPI.h>

// set I/O pins used in addition to clock, data in, data out
//const byte slaveSelectPin = 7;    // digital pin 10 for /CS
//const byte resetPin = 9;           // digital pin 9 for /RESET

const int SelectADC1 = 7;   // Temperature ADS1248 with 3x PT100
const int SelectADC2 = 6;   // Temperature ADS1248 with 3x PT100
const int SelectPRS  = 8;   // Pressure Sensor
const int SelectRTC  = 9;   // Real Time Clock
const int SelectSD   = 10;  // Micro SD card

unsigned long A2DVal=0x0;

void setup()
{
  //Enable Serial
  Serial.begin(9600);

  pinMode(SelectRTC, OUTPUT);
  pinMode(SelectPRS, OUTPUT);
  pinMode(SelectSD, OUTPUT);
  pinMode(SelectADC1, OUTPUT);
  pinMode(SelectADC2, OUTPUT);

  digitalWrite(SelectRTC, HIGH);
  digitalWrite(SelectPRS, HIGH);
  digitalWrite(SelectSD, HIGH);
  digitalWrite(SelectADC1, HIGH);
  digitalWrite(SelectADC2, HIGH);
 
  //pinMode (resetPin, OUTPUT);
  //digitalWrite(slaveSelectPin,HIGH);      // chip select is active low
  //digitalWrite(resetPin,HIGH);            // reset is active low
  SPI.begin(); //Turn on the SPI Bus
  SPIsettingsADC();
  setupADS1248(SelectADC1);
  setupADS1248(SelectADC2);


}

void SPIsettingsADC()
{
  Serial.print("setting ADS1248.... ");
  SPI.setDataMode(SPI_MODE1);
  delay(10);
  Serial.print("SPI_MODE1.... ");
  SPI.setBitOrder(MSBFIRST);
  delay(10);
  Serial.print("MSBFIRST.... ");
  SPI.setClockDivider(SPI_CLOCK_DIV8);
  delay(10);
  Serial.print("SPI_CLOCK_DIV8.... ");
  Serial.println(" done! ");
}

void setupADS1248(int CSPin)
{
  Serial.print("setup ADS1248.... ");

  digitalWrite(CSPin, LOW);
  delay(10);

  Serial.print(CSPin);

  SPI.transfer(0x06); //RESET
  delay(250); //Min. 0.6 ms
 
  Serial.print(" reset,.. ");

  SPI.transfer(0x16); // Stop reading continuosly
  delay(10);

  Serial.print(" stop reading,.. ");
  
  SPI.transfer(0x43); // Write to SYS0
  SPI.transfer(0x00);
  SPI.transfer(0x44); // PGA 16x, 80SPS
//  SPI.transfer(0x40); // PGA 16x, 5SPS
  delay(250);
  Serial.print(" write SYS0,.. ");
  
  SPI.transfer(0x42); // Write to MUX1
  SPI.transfer(0x00);
  SPI.transfer(0x28); // Int. oscl. ON, int. ref. ON, REF1, normal oper.
  delay(250);
  Serial.print(" write MUX1,.. ");
  
  SPI.transfer(0x4A); // Write to IDAC0
  SPI.transfer(0x00);
  SPI.transfer(0x06); // DRDY OFF, I1&I2 1mA
  delay(250);
  Serial.print(" write IDAC0,.. ");

  digitalWrite(CSPin, HIGH);
  delay(10);
  Serial.println(" done. ");

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
  
  digitalWrite(CSPin, LOW);
  delay(2000);
  Serial.println("slaveSelectPin,LOW ");

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
  delay(1000);
  
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
  delay(1000);
//  delay(800);
  
  SPI.transfer(0x12); // Read data once
  byteMSB = SPI.transfer(0xFF); // MSB
  Serial.print("byteMSB ");
  Serial.print(byteMSB);
  byteMID = SPI.transfer(0xFF); // Mid-Byte
  Serial.print("byteMID ");
  Serial.print(byteMID);
  byteLSB = SPI.transfer(0xFF); // LSB
  Serial.print("byteLSB ");
  Serial.println(byteLSB);
  outADC |= byteMSB;
  outADC <<= 8;
  outADC |= byteMID;
  outADC <<= 8;
  outADC |= byteLSB;
  Serial.print("byteMSB ");
  Serial.print(byteMSB);
  Serial.print("byteMID ");
  Serial.print(byteMID);
  Serial.print("byteLSB ");
  Serial.println(byteLSB);
  
  degC = (2.4 / 16.0) / (pow(2.0, 23.0) - 1.0) * float(outADC); // Voltage
  degC /= 1.0e-3; // Resistance
  degC = (degC - 100.0) / (3850e-6 * 100.0); // Temperature

  digitalWrite(CSPin, HIGH);
  delay(1000);
  Serial.println("slaveSelectPin,HIGH ");

  return degC;
}



void loop()
{
  float pt100t;
  char  pt100tChar[10];
  //digitalWrite(slaveSelectPin,LOW);      // chip select is active low
  delay(10);
  Serial.println("start ");
 
  SPI.transfer(0x4B); 
  SPI.transfer(0x00);
  SPI.transfer(0x8C); 
  for (int i=1; i <= 6; i++){
    pt100t = readADS1248(i);
    dtostrf(pt100t, 1, 3, pt100tChar);
    Serial.print (i);
    Serial.print (" , ");
    Serial.println(pt100tChar);
  } 
 
//  digitalWrite(slaveSelectPin,HIGH);      // chip select is active low
  
}
