#include <Servo.h>;
Servo servo1;

int pin = 9;    // pin de conexión PWM al servo
int pulsoMinimo = 580;  // Duración en microsegundos del pulso para girar 0º
int pulsoMaximo = 2500; // Duración en microsegundos del pulso para girar 180º
int angulo = 0; // Variable para guardar el angulo que deseamos de giro
int stop = 1500;

int velocidad_derecha = 1750;
int velocidad_izquierda = 1250;

int tiempo = 650;
int currentX = 0;
bool entradaCompleta = false;
String entradaSerial = "";

void setup()
{
  servo1.attach(pin, pulsoMinimo, pulsoMaximo);//, pulsoMinimo, pulsoMaximo);
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
      Serial.println("Recibido: " + entradaSerial);
      servo1.write(entradaSerial.toInt());
      entradaSerial = "";
    }
  }
}
 // From 0 to 360
void moveToAngle(int ang) {

}

void loop()
{
  servo1.write(stop);
  

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
