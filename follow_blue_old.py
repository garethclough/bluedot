import cv2
import numpy as np
import serial
import time

from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QTimer

COM = "COM8"
BAUD = 9600
PIXELS_PER_DEGREE = 2

ser = serial.Serial(COM, BAUD)

print("Available cameras:")

# Allow selecting of USB camera instead of using built in laptop camera
for i in range(5):
    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)

    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print(f"{i}: Camera available")

    cap.release()

camera = int(input("Select camera number: "))

cap = cv2.VideoCapture(camera)

if not cap.isOpened():
    print("Could not open camera")
    exit()

cv2.namedWindow("HSV Controls")

cv2.createTrackbar("H min", "HSV Controls", 90, 179, lambda x: None)
cv2.createTrackbar("H max", "HSV Controls", 120, 179, lambda x: None)
cv2.createTrackbar("S min", "HSV Controls", 100, 255, lambda x: None)
cv2.createTrackbar("S max", "HSV Controls", 255, 255, lambda x: None)
cv2.createTrackbar("V min", "HSV Controls", 20, 255, lambda x: None)
cv2.createTrackbar("V max", "HSV Controls", 255, 255, lambda x: None)

azulBajo = np.array([90, 100, 20], np.uint8)
azulAlto = np.array([120, 255, 255], np.uint8)
while True:
    ret, frame = cap.read()
    if ret:

        hMin = cv2.getTrackbarPos("H min", "HSV Controls")
        hMax = cv2.getTrackbarPos("H max", "HSV Controls")
        sMin = cv2.getTrackbarPos("S min", "HSV Controls")
        sMax = cv2.getTrackbarPos("S max", "HSV Controls")
        vMin = cv2.getTrackbarPos("V min", "HSV Controls")
        vMax = cv2.getTrackbarPos("V max", "HSV Controls")

        azulBajo = np.array([hMin, sMin, vMin], np.uint8)
        azulAlto = np.array([hMax, sMax, vMax], np.uint8)

  #      mascara = cv2.inRange(frameHSV, azulBajo, azulAlto)


        frame = cv2.flip(frame, 1)
        frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mascara = cv2.inRange(frameHSV, azulBajo, azulAlto)
        
        #Show mask to help setting colour range
        cv2.imshow("Mask", mascara)
        
        
        contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(frame, contornos, -1, (255, 0, 0), 4)

        windowHeight, windowWidth = frame.shape[:2]

        centreX = windowWidth // 2

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

            # Send to arduino
            dx = x - centreX
            angle = round(float(dx) / PIXELS_PER_DEGREE);
            print("Angle: "+ str(angle))
            ser.write((str(angle) + "\n").encode());

            cv2.putText(frame, '{},{}:  {}°'.format(x, y, angle), (x + 10, y), font, 1.2, (0, 0, 255), 2, cv2.LINE_AA)
            nuevoContorno = cv2.convexHull(c)
            cv2.drawContours(frame, [nuevoContorno], 0, (255, 0, 0), 3)

            # Wait for arduino
            while True:
                response = ser.readline().decode().strip()
                if response.startswith("DONE:"):
                    print("Arduino finished:", response)
                    break


        # cv2.imshow('mascaraAzul', mascara)
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            break
cap.release()
cv2.destroyAllWindows()

