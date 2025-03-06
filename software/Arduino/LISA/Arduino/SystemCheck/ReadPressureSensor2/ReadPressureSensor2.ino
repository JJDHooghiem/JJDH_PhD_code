#include <SPI.h>

// pins used for the connection with the sensor
// the other you need are controlled by the SPI library):

const int SelectSD      = 49;  // Micro SD card
const int SelectRTC     = 47;   // Real Time Clock
const int SelectPRS     = 45;   // Pressure Sensor
const int SelectPRS1    = 43;
const int SelectADC1    = 44;   // Temperature ADS1248 with 3x PT100
const int SelectADC2    = 46;   // Temperature ADS1248 with 3x PT100const int SelectADC2 = 6;   // Temperature ADS1248 with 3x PT100

const int chipSelectPin = SelectPRS1;

void setup() {
  Serial.begin(9600);

  // start the SPI library:
  SPI.begin();
  SPI.setClockDivider(128);
  // initalize the  data ready and chip select pins:
  //pinMode(dataReadyPin, INPUT);
  pinMode(chipSelectPin, OUTPUT);
  pinMode(SelectRTC, OUTPUT);
  pinMode(SelectSD, OUTPUT);
  pinMode(SelectADC1, OUTPUT);
  pinMode(SelectADC2, OUTPUT);
  pinMode(SelectPRS, OUTPUT);
  
  
  digitalWrite(chipSelectPin,HIGH);
  digitalWrite(SelectRTC,HIGH);
  digitalWrite(SelectSD,HIGH);
  digitalWrite(SelectRTC,HIGH);
  digitalWrite(SelectADC1,HIGH);
  digitalWrite(SelectADC2,HIGH);
  digitalWrite(SelectPRS,HIGH);
 
  delay(100);
}

void loop()
{
  SPI.setClockDivider(SPI_CLOCK_DIV32);

  digitalWrite(chipSelectPin,LOW);
  delay(500);
 
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
  
  digitalWrite(chipSelectPin,HIGH);
  delay(1000); 
}





