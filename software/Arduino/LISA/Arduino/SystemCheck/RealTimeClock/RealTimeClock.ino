#include <SPI.h>

const int SelectSD      = 49;  // Micro SD card
const int SelectRTC     = 47;   // Real Time Clock
const int SelectPRS     = 45;   // Pressure Sensor
const int SelectPRS2    = 43;
const int SelectADC1    = 44;   // Temperature ADS1248 with 3x PT100
const int SelectADC2    = 46;   // Temperature ADS1248 with 3x PT100

const int cs            = SelectRTC; //chip select 


void setup() {
  Serial.begin(9600);

  Serial.println(" setup ");

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

  RTC_init();
  //day(1-31), month(1-12), year(0-99), hour(0-23), minute(0-59), second(0-59)
  SetTimeDate(12,03,15,23,55,00); 
}

void loop() {
  Serial.println(ReadTimeDate());
  delay(1000);
}
//=====================================
int RTC_init(){ 
	  pinMode(cs,OUTPUT); // chip select
	  // start the SPI library:
	  SPI.begin();
	  SPI.setBitOrder(MSBFIRST); 
	  SPI.setDataMode(SPI_MODE3); // both mode 1 & 3 should work 
	  //set control register 
	  digitalWrite(cs, LOW);  
	  SPI.transfer(0x8E);
	  SPI.transfer(0x60); //60= disable Osciallator and Battery SQ wave @1hz, temp compensation, Alarms disabled
	  digitalWrite(cs, HIGH);
	  delay(10);
}
//=====================================
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
		  
		digitalWrite(cs, LOW);
		SPI.transfer(i+0x80); 
		SPI.transfer(TimeDate[i]);        
		digitalWrite(cs, HIGH);
  }
}
//=====================================
String ReadTimeDate(){
	String temp;
	int TimeDate [7]; //second,minute,hour,null,day,month,year		
	for(int i=0; i<=6;i++){
		if(i==3)
			i++;
		digitalWrite(cs, LOW);
		SPI.transfer(i+0x00); 
		unsigned int n = SPI.transfer(0x00);        
		digitalWrite(cs, HIGH);
		int a=n & B00001111;    
		if(i==2){	
			int b=(n & B00110000)>>4; //24 hour mode
			if(b==B00000010)
				b=20;        
			else if(b==B00000001)
				b=10;
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
	temp.concat(TimeDate[4]);
	temp.concat("/") ;
	temp.concat(TimeDate[5]);
	temp.concat("/") ;
	temp.concat(TimeDate[6]);
	temp.concat("     ") ;
	temp.concat(TimeDate[2]);
	temp.concat(":") ;
	temp.concat(TimeDate[1]);
	temp.concat(":") ;
	temp.concat(TimeDate[0]);
  return(temp);
}
