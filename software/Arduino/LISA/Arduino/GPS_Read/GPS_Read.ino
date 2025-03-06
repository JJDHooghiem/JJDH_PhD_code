/*
  Mega multple serial test

Receives from the main serial port, sends to the others.
Receives from serial port 1, sends to the main serial (Serial 0).

This example works only on the Arduino Mega

The circuit:
* Any serial device attached to Serial port 1
* Serial monitor open on Serial port 0:

created 30 Dec. 2008
by Tom Igoe

This example code is in the public domain.

*/
#include <TinyGPS.h>

TinyGPS gps; // create gps object
long lat,lon; // create variable for latitude and longitude object
float flat, flon;
unsigned long age, date, time, chars = 0;

static void smartdelay(unsigned long ms);
static void print_date(TinyGPS &gps);
static void print_int(unsigned long val, unsigned long invalid, int len);

void setup() {
  // initialize both serial ports:
  Serial.begin(9600);
  Serial1.begin(9600);

/// note this line which "primes the pump"  otherwise you get nothing...
  Serial.print("a");

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

static void smartdelay(unsigned long ms)
{
  unsigned long start = millis();
  do { while (Serial1.available()) gps.encode(Serial1.read());
  } while (millis() - start < ms);
}


void loop(){
  while(Serial1.available()){ // check for gps data
   if(gps.encode(Serial1.read())){ // encode gps data
    gps.get_position(&lat,&lon); // get latitude and longitude
    // display position
    Serial.print("Position: ");
    Serial.print("lat: ");Serial.print(lat);Serial.print(" ");// print latitude
    Serial.print("lon: ");Serial.println(lon); // print longitude
    gps.f_get_position(&flat,&flon, &age); // get latitude and longitude
    // display position
    Serial.print("Position: ");
    Serial.print("flat: ");Serial.print(flat);Serial.print(" ");// print latitude
    Serial.print("flon: ");Serial.print(flon);Serial.print(" ");// print latitude
    Serial.print("age: ");Serial.println(age); // print longitude
//    void TinyGPS::get_datetime(unsigned long *date, unsigned long *time, unsigned long *age)
    print_date(gps);
   }
  }
}


