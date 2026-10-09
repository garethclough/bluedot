import sys
import cv2
import numpy as np
import serial
import time

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QSlider,
    QComboBox,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QGroupBox
)

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap


# ---------------------------------------------------------
# Settings
# ---------------------------------------------------------

COM = "COM8"
BAUD = 9600
MAX_PIXELS_PER_DEGREE = 5
MAX_WAIT_FOR_ARDUINO = 1.0


# ---------------------------------------------------------
# Main window
# ---------------------------------------------------------

class FollowColourWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Colour Tracker")
        self.resize(1200, 800)

        # Camera
        self.cap = None

        # Arduino
        self.ser = serial.Serial(COM, BAUD, timeout=0)

        # Prevent sending another command while Arduino is moving
        self.waitingForArduino = False
        self.nextAngle = False
        self.arduinoTime = False

        # -------------------------------------------------
        # Camera selection
        # -------------------------------------------------

        self.cameraCombo = QComboBox()
        self.cameraCombo.addItem("Select camera")

        for i in range(5):
            testCap = cv2.VideoCapture(i, cv2.CAP_DSHOW)

            if testCap.isOpened():
                ret, frame = testCap.read()

                if ret:
                    self.cameraCombo.addItem(f"Camera {i}", i)

            testCap.release()

        self.cameraCombo.currentIndexChanged.connect(self.selectCamera)

        # -------------------------------------------------
        # Video labels
        # -------------------------------------------------

        self.cameraLabel = QLabel()
        self.cameraLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cameraLabel.setMinimumSize(500, 350)
        self.cameraLabel.setStyleSheet("background-color: black;")

        self.maskLabel = QLabel()
        self.maskLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.maskLabel.setMinimumSize(500, 350)
        self.maskLabel.setStyleSheet("background-color: black;")

        # -------------------------------------------------
        # HSV sliders
        # -------------------------------------------------

        self.hMin = self.createSlider(0, 179, 90)
        self.hMax = self.createSlider(0, 179, 120)

        self.sMin = self.createSlider(0, 255, 100)
        self.sMax = self.createSlider(0, 255, 255)

        self.vMin = self.createSlider(0, 255, 20)
        self.vMax = self.createSlider(0, 255, 255)

        # Options
        self.pixelsPerTenthOfDegree = 2

        # -------------------------------------------------
        # Information labels
        # -------------------------------------------------

        self.positionLabel = QLabel("X: --    Y: --")
        self.angleLabel = QLabel("Angle: --°")
        self.areaLabel = QLabel("Area: --")
        self.arduinoLabel = QLabel("Arduino: Ready")

        # -------------------------------------------------
        # Buttons
        # -------------------------------------------------

        self.startButton = QPushButton("Start")
        self.stopButton = QPushButton("Stop")

        self.startButton.clicked.connect(self.startCamera)
        self.stopButton.clicked.connect(self.stopCamera)

        # -------------------------------------------------
        # Timer
        # -------------------------------------------------

        self.timer = QTimer()
        self.timer.timeout.connect(self.updateFrame)

        self.arduinoTimer = QTimer()
        self.arduinoTimer.timeout.connect(self.updateArduino)
        self.arduinoTimer.start(200) 


        # -------------------------------------------------
        # Layout
        # -------------------------------------------------

        mainLayout = QVBoxLayout()

        # Camera selection
        cameraLayout = QHBoxLayout()

        cameraLayout.addWidget(QLabel("Camera:"))
        cameraLayout.addWidget(self.cameraCombo)
        cameraLayout.addStretch()
        cameraLayout.addWidget(self.startButton)
        cameraLayout.addWidget(self.stopButton)

        mainLayout.addLayout(cameraLayout)

        # Camera + mask
        videoLayout = QHBoxLayout()

        cameraGroup = QGroupBox("Camera")
        cameraGroupLayout = QVBoxLayout()
        cameraGroupLayout.addWidget(self.cameraLabel)
        cameraGroup.setLayout(cameraGroupLayout)

        maskGroup = QGroupBox("Mask")
        maskGroupLayout = QVBoxLayout()
        maskGroupLayout.addWidget(self.maskLabel)
        maskGroup.setLayout(maskGroupLayout)

        videoLayout.addWidget(cameraGroup)
        videoLayout.addWidget(maskGroup)

        mainLayout.addLayout(videoLayout)

        # HSV controls
        hsvGroup = QGroupBox("HSV Colour Range")
        hsvLayout = QGridLayout()

        hsvLayout.addWidget(QLabel("H min"), 0, 0)
        hsvLayout.addWidget(self.hMin, 0, 1)

        hsvLayout.addWidget(QLabel("H max"), 1, 0)
        hsvLayout.addWidget(self.hMax, 1, 1)

        hsvLayout.addWidget(QLabel("S min"), 2, 0)
        hsvLayout.addWidget(self.sMin, 2, 1)

        hsvLayout.addWidget(QLabel("S max"), 3, 0)
        hsvLayout.addWidget(self.sMax, 3, 1)

        hsvLayout.addWidget(QLabel("V min"), 4, 0)
        hsvLayout.addWidget(self.vMin, 4, 1)

        hsvLayout.addWidget(QLabel("V max"), 5, 0)
        hsvLayout.addWidget(self.vMax, 5, 1)

        hsvGroup.setLayout(hsvLayout)
        mainLayout.addWidget(hsvGroup)

        # Settings
        self.pixelsPerDegreeSlider = self.createSlider(1,100,20)
        self.pixelsPerDegreeLabel = QLabel(str(float(self.pixelsPerDegreeSlider.value()) / 10.0) + " pixels/degree")
        self.pixelsPerDegreeSlider.valueChanged.connect(
            lambda value: self.pixelsPerDegreeLabel.setText(
                f"{value / 10:.1f} pixels/degree"
            )
        )

        settingsGroup = QGroupBox("Settings")
        settingsLayout = QGridLayout()
        settingsLayout.addWidget(QLabel("Pixels per degree"), 0, 0)
        settingsLayout.addWidget(self.pixelsPerDegreeSlider, 0, 1)
        settingsLayout.addWidget(self.pixelsPerDegreeLabel, 0, 2)
        self.arduinoTimerSlider = self.createSlider(1,1000,200)
        self.arduinoTimerSliderLabel = QLabel(str(self.arduinoTimerSlider.value()) + ' ms')
        self.arduinoTimerSlider.valueChanged.connect(
            self.updateArduinoTimer
        )


        settingsLayout.addWidget(QLabel("Arduino Message Fequency"), 1, 0)
        settingsLayout.addWidget(self.arduinoTimerSlider, 1, 1)
        settingsLayout.addWidget(self.arduinoTimerSliderLabel, 1, 2)


        settingsGroup.setLayout(settingsLayout)
        mainLayout.addWidget(settingsGroup)


        

        # Information
        infoLayout = QHBoxLayout()

        infoLayout.addWidget(self.positionLabel)
        infoLayout.addWidget(self.angleLabel)
        infoLayout.addWidget(self.areaLabel)
        infoLayout.addWidget(self.arduinoLabel)

        mainLayout.addLayout(infoLayout)

        self.setLayout(mainLayout)

    # -----------------------------------------------------
    # Callback from slider
    # -----------------------------------------------------
    def updateArduinoTimer(self, value):
        self.arduinoTimerSliderLabel.setText(f"{value} ms")
        self.arduinoTimer.setInterval(value)


    # -----------------------------------------------------
    # Create slider
    # -----------------------------------------------------

    def createSlider(self, minimum, maximum, value):

        slider = QSlider(Qt.Orientation.Horizontal)

        slider.setMinimum(minimum)
        slider.setMaximum(maximum)
        slider.setValue(value)

        return slider

    # -----------------------------------------------------
    # Camera selection
    # -----------------------------------------------------

    def selectCamera(self):

        cameraIndex = self.cameraCombo.currentData()

        if cameraIndex is None:
            return

        self.stopCamera()

        self.cap = cv2.VideoCapture(
            cameraIndex,
            cv2.CAP_DSHOW
        )

        if self.cap.isOpened():

            self.arduinoLabel.setText(
                f"Camera {cameraIndex} selected"
            )

            self.startCamera()

        else:

            self.arduinoLabel.setText(
                "Could not open camera"
            )

    # -----------------------------------------------------
    # Start camera
    # -----------------------------------------------------

    def startCamera(self):

        if self.cap is None:
            return

        if not self.cap.isOpened():
            return

        self.timer.start(30)

    # -----------------------------------------------------
    # Stop camera
    # -----------------------------------------------------

    def stopCamera(self):

        self.timer.stop()

        if self.cap is not None:

            self.cap.release()
            self.cap = None

        self.cameraLabel.clear()
        self.maskLabel.clear()

    # -----------------------------------------------------
    # Convert OpenCV image to Qt image
    # -----------------------------------------------------

    def displayImage(self, image, label):

        if len(image.shape) == 2:

            image = cv2.cvtColor(
                image,
                cv2.COLOR_GRAY2RGB
            )

        else:

            image = cv2.cvtColor(
                image,
                cv2.COLOR_BGR2RGB
            )

        height, width, channels = image.shape
        bytesPerLine = channels * width

        qtImage = QImage(
            image.data,
            width,
            height,
            bytesPerLine,
            QImage.Format.Format_RGB888
        )

        pixmap = QPixmap.fromImage(qtImage)

        label.setPixmap(
            pixmap.scaled(
                label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )

    # -----------------------------------------------------
    # Main camera processing
    # -----------------------------------------------------

    def updateFrame(self):

        if self.cap is None:
            return

        ret, frame = self.cap.read()

        if not ret:
            return

        # Mirror image
        frame = cv2.flip(frame, 1)

        # -------------------------------------------------
        # HSV
        # -------------------------------------------------

        frameHSV = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2HSV
        )

        hMin = self.hMin.value()
        hMax = self.hMax.value()

        sMin = self.sMin.value()
        sMax = self.sMax.value()

        vMin = self.vMin.value()
        vMax = self.vMax.value()

        lower = np.array(
            [hMin, sMin, vMin],
            np.uint8
        )

        upper = np.array(
            [hMax, sMax, vMax],
            np.uint8
        )

        mask = cv2.inRange(
            frameHSV,
            lower,
            upper
        )

        # -------------------------------------------------
        # Find contours
        # -------------------------------------------------

        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        # Camera centre
        windowHeight, windowWidth = frame.shape[:2]

        centreX = windowWidth // 2
        centreY = windowHeight // 2

        # Draw camera centre
        cv2.circle(
            frame,
            (centreX, centreY),
            7,
            (0, 255, 0),
            -1
        )

        # -------------------------------------------------
        # Find largest contour
        # -------------------------------------------------

        areaMax = 0
        contourMax = None

        for c in contours:

            area = cv2.contourArea(c)

            if area > areaMax:

                areaMax = area
                contourMax = c

        # -------------------------------------------------
        # Process largest contour
        # -------------------------------------------------

        if contourMax is not None:

            c = contourMax

            M = cv2.moments(c)

            if M["m00"] != 0:

                x = int(
                    M["m10"] / M["m00"]
                )

                y = int(
                    M["m01"] / M["m00"]
                )

                # Draw object centre
                cv2.circle(
                    frame,
                    (x, y),
                    7,
                    (0, 0, 255),
                    -1
                )

                # Draw contour
                cv2.drawContours(
                    frame,
                    [c],
                    -1,
                    (255, 0, 0),
                    3
                )

                # Convex hull
                hull = cv2.convexHull(c)

                cv2.drawContours(
                    frame,
                    [hull],
                    0,
                    (255, 0, 0),
                    2
                )

                # -------------------------------------------------
                # Calculate angle
                # -------------------------------------------------

                dx = x - centreX

                # Slider values are tenths of a degree
                angle = round(
                    float(dx) / (float(self.pixelsPerDegreeSlider.value()) / 10.0)
                )

                # -------------------------------------------------
                # Display information
                # -------------------------------------------------

                self.positionLabel.setText(
                    f"X: {x}    Y: {y}"
                )

                self.angleLabel.setText(
                    f"Angle: {angle}°"
                )

                self.areaLabel.setText(
                    f"Area: {areaMax:.1f}"
                )

                # Draw text on camera
                cv2.putText(
                    frame,
                    f"{x},{y}: {angle}°",
                    (x + 10, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (0, 0, 255),
                    2,
                    cv2.LINE_AA
                )

                # -------------------------------------------------
                # Set angle to send to Arduino
                # -------------------------------------------------
                self.nextAngle = angle

 
        else:

            self.positionLabel.setText(
                "X: --    Y: --"
            )

            self.angleLabel.setText(
                "Angle: --°"
            )

            self.areaLabel.setText(
                "Area: --"
            )

        # -------------------------------------------------
        # Display images
        # -------------------------------------------------

        self.displayImage(
            frame,
            self.cameraLabel
        )

        self.displayImage(
            mask,
            self.maskLabel
        )

    # -----------------------------------------------------
    # Close window
    # -----------------------------------------------------

    def closeEvent(self, event):

        self.timer.stop()

        if self.cap is not None:
            self.cap.release()

        if self.ser.is_open:
            self.ser.close()

        event.accept()

    def updateArduino(self):
        if self.waitingForArduino:
            while self.ser.in_waiting:
                response = self.ser.readline().decode().strip()
                if response.startswith("DONE:"):
                    print("Arduino finished:", response)
                    self.waitingForArduino = False

        # Dont wait indefinitely for arduino response
        currentTime = time.perf_counter()
        if self.waitingForArduino and self.arduinoTime is not False and currentTime - self.arduinoTime > MAX_WAIT_FOR_ARDUINO:
            self.waitingForArduino = False
            print("No response from arduino")


        if not self.waitingForArduino and self.nextAngle is not False:
            angle = self.nextAngle
            print("Angle: "+ str(angle))
            self.ser.write((str(angle) + "\n").encode());
            self.arduinoTime = time.perf_counter()
            self.waitingForArduino = True

            self.arduinoLabel.setText(
                f"Arduino: Moving to {angle}°"
            )
            self.nextAngle = False


# ---------------------------------------------------------
# Start application
# ---------------------------------------------------------

app = QApplication(sys.argv)

window = FollowColourWindow()
window.show()

sys.exit(app.exec())
