#include <Servo.h>;
Servo servo1;

int pin = 9;    // pin de conexión PWM al servo
int pulsoMinimo = 580;  // Duración en microsegundos del pulso para girar 0º
int pulsoMaximo = 2500; // Duración en microsegundos del pulso para girar 180º
int angulo = 0; // Variable para guardar el angulo que deseamos de giro
int stop = 1500;

int velocidad_derecha = 1750;
int velocidad_izquierda = 1250;
int millisecondsToTurn180 = 450; 

int tiempo = 650;
int currentX = 0;
bool entradaCompleta = false;
String entradaSerial = "";
int currentAngle = 0;

void setup()
{
  servo1.attach(pin, pulsoMinimo, pulsoMaximo);
  servo1.write(stop);
  Serial.begin(9600);
}

void serialEvent() {
  while (Serial.available()) {
    // Obtener bytes de entrada:
    char inChar = (char)Serial.read();
    entradaSerial += inChar;
    

    if (inChar == '\n') {
      entradaCompleta = true;
      int intAngle = entradaSerial.toInt();
//      Serial.println("Recibido: " + intAngle);
      moveToAngle(intAngle);
      entradaSerial = "";
    }
  }
}
 // From 0 to 360
void moveToAngle(int ang) {
  if (currentAngle == ang) {
    Serial.print("DONE:");
    Serial.println(currentAngle);
    return;
  }

  int changeAngle = ang - currentAngle;
  float changeTimePerDegree = millisecondsToTurn180 / 180.0;
  float changeTime = 0;
  if (changeAngle > 0) {
    changeTime = (float)changeAngle * changeTimePerDegree;
    servo1.write(velocidad_derecha);
    delay(lround(changeTime));
    servo1.write(stop);
  } else {
    changeTime = (float)-changeAngle * changeTimePerDegree;
    servo1.write(velocidad_izquierda);
    delay(lround(changeTime));
    servo1.write(stop);
  }   
  currentAngle = ang;
  Serial.print("DONE:");
  Serial.println(currentAngle);
}

void loop()
{

  /*
  servo1.write(180);
//  moveToAngle(180);
  delay(pulsoMaximo);
  servo1.write(stop);
  delay(8000);
*/
  /*
    servo1.write(0);
    delay(1000);
    servo1.write(30);
    delay(1000);
    servo1.write(60);
    delay(1000);
    servo1.write(90);
    delay(1000);
    servo1.write(120);
    delay(1000);
    servo1.write(150);
    delay(1000);
    servo1.write(180);
    delay(1000);
    servo1.write(velocidad_derecha);
    delay(tiempo);
    servo1.write(stop);
    delay(tiempo);
    servo1.write(velocidad_izquierda);
    delay(tiempo);
    servo1.write(stop);
    delay(tiempo);
    */
}
