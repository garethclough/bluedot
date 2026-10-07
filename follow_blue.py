import cv2
import numpy as np
import serial
import time

COM = "COM8"
BAUD = 9600
ser = serial.Serial(COM, BAUD)

cap = cv2.VideoCapture(0)
azulBajo = np.array([90, 100, 20], np.uint8)
azulAlto = np.array([120, 255, 255], np.uint8)
while True:
    ret, frame = cap.read()
    if ret:
        frame = cv2.flip(frame, 1)
        frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mascara = cv2.inRange(frameHSV, azulBajo, azulAlto)
        contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(frame, contornos, -1, (255, 0, 0), 4)

        # Get biggest area
        areaMax = 0
        contourMax = None
        currentX = None
        
        for c in contornos:
            area = cv2.contourArea(c)
            if area > areaMax:
                areaMax = area
                contourMax = c


        if contourMax is not None:
            print("Max area: " + str(areaMax))
            c = contourMax
            M = cv2.moments(c)
            if M["m00"] == 0:
                M["m00"] = 1
            x = int(M["m10"] / M["m00"])
            
            y = int(M['m01'] / M['m00'])
            cv2.circle(frame, (x, y), 7, (0, 0, 255), -1)
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame, '{},{}'.format(x, y), (x + 10, y), font, 1.2, (0, 0, 255), 2, cv2.LINE_AA)
            nuevoContorno = cv2.convexHull(c)
            cv2.drawContours(frame, [nuevoContorno], 0, (255, 0, 0), 3)

            print("x "+str(x))
            ser.write(x);
            

        # cv2.imshow('mascaraAzul', mascara)
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            break
cap.release()
cv2.destroyAllWindows()

