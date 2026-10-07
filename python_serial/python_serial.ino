String entradaSerial = "";         // String para almacenar entrada
bool entradaCompleta = false;  // Indicar si el String está completo

void setup()
{
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH);  
  Serial.begin(9600);
}

void loop()
{
  if (entradaCompleta) {
    if(entradaSerial == "ON\n"){
      Serial.print("ON recibido\n");
      digitalWrite(LED_BUILTIN, HIGH);
    }
    else if(entradaSerial == "OFF\n"){
      Serial.print("OFF recibido\n");
      digitalWrite(LED_BUILTIN, LOW);
    }
    else { // Cualquier otro dato recibido
      Serial.println("El dato recibido es inválido!!");
    }
    entradaSerial = "";
    entradaCompleta = false;
  }
}

// Función que se activa al recibir algo por
// el puerto serie, Interrupción del Puerto Serie.
void serialEvent() {
  while (Serial.available()) {
    // Obtener bytes de entrada:
    char inChar = (char)Serial.read();
    // Agregar al String de entrada:
    entradaSerial += inChar;
    // Para saber si el string está completo, se detendrá al recibir
    // el caracter de retorno de línea ENTER \n
    if (inChar == '\n') {
      entradaCompleta = true;
    }
  }
}
