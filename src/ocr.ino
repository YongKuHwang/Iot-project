#include <LiquidCrystal.h>
#include <Servo.h>
LiquidCrystal lcd(4, 6, 10, 11, 12, 13); // LCD 핀 설정에 맞게 변경
Servo servoMotor;
String dong;
String cmd;
void setup() {
  Serial.begin(9600);
  lcd.begin(16, 2); // LCD의 행과 열 개수에 맞게 변경
  servoMotor.attach(9); // 서보 모터 핀 번호에 맞게 변경
  }
void loop() {
  if(Serial.available()){
    cmd = Serial.readString();
    cmd.trim(); // Remove leading/trailing whitespace
    int cmdLength = cmd.length();
    dong = cmd.substring((cmdLength-3) % cmdLength, min((cmdLength-3) % cmdLength + 16, cmdLength));
    servoLoop(dong.toInt());
    for(int i = 0; i < cmdLength; i++)
    {
      lcd.clear();
      lcd.setCursor(0, 0);
      // Calculate the substring based on the current index and length
      String displayText = cmd.substring(i % cmdLength, min(i % cmdLength + 16, cmdLength));
      lcd.print(displayText);
      delay(500);
    }
  }
}
 void servoLoop(int dong) {
   if (dong == 101) {
     moveServo(0);
   }
   else if (dong == 102) {
     moveServo(60);
   }
   else if (dong == 103) {
     moveServo(120);
   }
   else if (dong == 104) {
     moveServo(180);
   }
 }
 void moveServo(int angle) {
   servoMotor.write(angle);
   delay(500);
 }