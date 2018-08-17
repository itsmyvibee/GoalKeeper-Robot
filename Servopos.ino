  //int delay =1000; //delay;
#include <Servo.h>

Servo myservo;  // create servo object to control a servo

void setup() {
  Serial.begin(9600); //starta porta serial
  myservo.attach(10);  // attaches the servo on pin 9 to the servo object
}

void loop() {
  while(Serial.available()==0){}; //espera por info pela porta serial
  int pos = Serial.read(); // le a porta serial
  Serial.print(pos);
  
  //delay(2000);
  
  myservo.write(pos);                  // sets the servo position according to the scaled value
  
  
}



