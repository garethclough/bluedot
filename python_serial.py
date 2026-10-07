import serial
import time

COM = "COM7"
BAUD = 9600
ser = serial.Serial(COM, BAUD)

print("Se envía el on\n")
ser.write(b"ON\n")

time.sleep(5)
print("Se envía el off\n")
ser.write(b"OFF\n")

