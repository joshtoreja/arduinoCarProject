#include <Arduino.h>
#include <IRremote.hpp>

#define L_PWM 5
#define L_IN1 2
#define L_IN2 4
#define R_PWM 6
#define R_IN1 7
#define R_IN2 8

#define IR_RECV_PIN 12
#define IR_CODE_9  0xFF52AD
#define IR_CODE_EXIT 0xFF9867

enum Heading { NORTH=0, EAST=1, SOUTH=2, WEST=3 };
Heading heading = NORTH;

int DRIVE_SPEED = 180;
int TURN_SPEED  = 170;
unsigned long CELL_MS   = 600;
unsigned long TURN90_MS = 350;

bool path_mode = false;
String lineBuf;

void stopMotors() {
  analogWrite(L_PWM, 0); analogWrite(R_PWM, 0);
  digitalWrite(L_IN1, LOW); digitalWrite(L_IN2, LOW);
  digitalWrite(R_IN1, LOW); digitalWrite(R_IN2, LOW);
}
void leftMotor(int s) {
  if (s == 0) { digitalWrite(L_IN1, LOW); digitalWrite(L_IN2, LOW); analogWrite(L_PWM, 0); }
  else if (s > 0) { digitalWrite(L_IN1, HIGH); digitalWrite(L_IN2, LOW); analogWrite(L_PWM, min(s,255)); }
  else { digitalWrite(L_IN1, LOW); digitalWrite(L_IN2, HIGH); analogWrite(L_PWM, min(-s,255)); }
}
void rightMotor(int s) {
  if (s == 0) { digitalWrite(R_IN1, LOW); digitalWrite(R_IN2, LOW); analogWrite(R_PWM, 0); }
  else if (s > 0) { digitalWrite(R_IN1, HIGH); digitalWrite(R_IN2, LOW); analogWrite(R_PWM, min(s,255)); }
  else { digitalWrite(R_IN1, LOW); digitalWrite(R_IN2, HIGH); analogWrite(R_PWM, min(-s,255)); }
}
void driveForwardMs(unsigned long ms) { leftMotor(DRIVE_SPEED); rightMotor(DRIVE_SPEED); delay(ms); stopMotors(); delay(80); }
void turnLeft90()  { leftMotor(-TURN_SPEED); rightMotor(TURN_SPEED); delay(TURN90_MS); stopMotors(); delay(100); heading = (Heading)((4 + heading - 1) % 4); }
void turnRight90() { leftMotor(TURN_SPEED); rightMotor(-TURN_SPEED); delay(TURN90_MS); stopMotors(); delay(100); heading = (Heading)((heading + 1) % 4); }
void turnAround180(){ leftMotor(TURN_SPEED); rightMotor(-TURN_SPEED); delay(2*TURN90_MS); stopMotors(); delay(120); heading = (Heading)((heading + 2) % 4); }
void faceHeading(Heading t){ int d = ((int)t - (int)heading + 4) % 4; if (d==1) turnRight90(); else if (d==2) turnAround180(); else if (d==3) turnLeft90(); }
void moveCells(int n){ for (int i=0;i<n;i++) driveForwardMs(CELL_MS); }

void enterPathMode(){ path_mode = true; heading = NORTH; stopMotors(); Serial.println("PATH:ENTER"); }
void exitPathMode(){  path_mode = false; stopMotors(); Serial.println("PATH:EXIT"); }

bool parseDirCount(const String& s, char& dir, int& count){
  if (!s.length()) return false;
  dir = toupper(s.charAt(0));
  if (dir!='U' && dir!='D' && dir!='L' && dir!='R') return false;
  if (s.length()==1){ count=1; return true; }
  long c = s.substring(1).toInt(); if (c<=0) c=1; count=(int)c; return true;
}
void pathModeStep(){
  while (Serial.available()){
    char ch = Serial.read();
    if (ch=='\n' || ch=='\r'){
      if (!lineBuf.length()) continue;
      String line=lineBuf; line.trim(); lineBuf="";
      if (line.equalsIgnoreCase("S")) { heading=NORTH; stopMotors(); }
      else if (line.equalsIgnoreCase("E")) { stopMotors(); exitPathMode(); }
      else if (line.equalsIgnoreCase("X")) { exitPathMode(); }
      else {
        char d; int n;
        if (parseDirCount(line,d,n)){
          Heading tgt=heading;
          if (d=='U') tgt=NORTH; else if (d=='R') tgt=EAST; else if (d=='D') tgt=SOUTH; else if (d=='L') tgt=WEST;
          faceHeading(tgt); moveCells(n);
        }
      }
    } else lineBuf += ch;
  }
}

void IR_begin(){ IrReceiver.begin(IR_RECV_PIN, ENABLE_LED_FEEDBACK); }
bool IR_read(uint32_t &raw, uint8_t &cmd){
  if (IrReceiver.decode()){
    raw = IrReceiver.decodedIRData.decodedRawData;
    cmd = IrReceiver.decodedIRData.command;
    IrReceiver.resume();
    return true;
  }
  return false;
}
void checkIR(){
  uint32_t raw; uint8_t cmd;
  if (!IR_read(raw, cmd)) return;
  if (cmd == 9 || raw == IR_CODE_9) enterPathMode();
  if (raw == IR_CODE_EXIT || cmd == 0) if (path_mode) exitPathMode();
}

void setup(){
  pinMode(L_PWM,OUTPUT); pinMode(L_IN1,OUTPUT); pinMode(L_IN2,OUTPUT);
  pinMode(R_PWM,OUTPUT); pinMode(R_IN1,OUTPUT); pinMode(R_IN2,OUTPUT);
  stopMotors();
  Serial.begin(115200);
  delay(50);
  Serial.println("RDY");
  IR_begin();
}
void loop(){
  if (path_mode){ pathModeStep(); return; }
  checkIR();
}
