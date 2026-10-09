#include <Servo.h>

Servo servo1;

const int pin = 9;
const int minimumPulse = 580;
const int maximumPulse = 2500;

const int stopPulse = 1500;
const int rightSpeed = 1750;
const int leftSpeed = 1250;

const float millisecondsToTurn180 = 450.0;

String serialInput = "";

int currentAngle = 0;
int targetAngle = 0;

unsigned long movementStartTime = 0;
unsigned long movementDuration = 0;

bool isMoving = false;

void setup()
{
  servo1.attach(pin, minimumPulse, maximumPulse);
  servo1.writeMicroseconds(stopPulse);
  Serial.begin(9600);
}

void loop()
{
  readSerial();
  updateMovement();
}

void readSerial()
{
  while (Serial.available())
  {
    char inputChar = (char)Serial.read();

    if (inputChar == '\n')
    {
      int angle = serialInput.toInt();
      serialInput = "";
      Serial.print("RECEIVED:");
      Serial.println(currentAngle);

      moveToAngle(angle);
    }
    else if (inputChar != '\r')
    {
      serialInput += inputChar;
    }
  }
}

void moveToAngle(int angle)
{
  // Estimate the current position if already moving
  if (isMoving)
  {
    unsigned long elapsedTime = millis() - movementStartTime;

    float fraction = (float)elapsedTime / movementDuration;
    fraction = constrain(fraction, 0.0, 1.0);

    int angleChange = targetAngle - currentAngle;
    currentAngle += round(angleChange * fraction);
  }

  targetAngle = angle;

  int angleChange = targetAngle - currentAngle;

  if (angleChange == 0)
  {
    servo1.writeMicroseconds(stopPulse);
    isMoving = false;
    return;
  }

  movementDuration = (unsigned long)(
    abs(angleChange) * millisecondsToTurn180 / 180.0
  );

  movementStartTime = millis();
  isMoving = true;

  if (angleChange > 0)
    servo1.write(rightSpeed);
  else
    servo1.write(leftSpeed);
}

void updateMovement()
{
  if (!isMoving)
    return;

  if (millis() - movementStartTime >= movementDuration)
  {
    servo1.writeMicroseconds(stopPulse);

    currentAngle = targetAngle;
    isMoving = false;

    Serial.print("DONE:");
    Serial.println(currentAngle);
  }
}