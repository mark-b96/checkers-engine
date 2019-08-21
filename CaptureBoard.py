import numpy as np
import cv2
import math
import ASUS.GPIO as GPIO
import time


class CaptureBoard(object):
    def __init__(self):
        self.corner_coordinates = []

    def initialise_camera(self):
        cv2.setNumThreads(4)
        faceCascade = cv2.CascadeClassifier("/usr/local/share/OpenCV/haarcascades//haarcascade_frontalface_alt.xml")
        cap = cv2.VideoCapture(
            "rkcamsrc io-mode=4 isp-mode=2A tuning-xml-path=/etc/cam_iq/IMX219.xml ! video/x-raw,format=NV12,width=640,height=480 ! videoconvert ! appsink")
        return cap

    def pin_setup(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(37, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Push-button pin with pull-up resistor
        GPIO.setup(11, GPIO.OUT)  # Red LED output
        GPIO.setup(21, GPIO.OUT)  # Green LED output

    def calibrate_board(self, cap):
        ret, frame = cap.read()
        grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert image to greyscale
        img_cal = grey
        cv2.imwrite('/home/linaro/Pictures/calibrated_board.png', img_cal)
        ret, corners = cv2.findChessboardCorners(grey, (7, 7), None)
        print("Attempting to calibrate board")
        if ret:
            print("Calibrating Board")
            self.corner_coordinates.append(corners)
            img_grid = cv2.drawChessboardCorners(grey, (7, 7), corners, ret)
            cv2.imwrite('/home/linaro/Pictures/corners.png', img_grid)
            self.corner_coordinates = self.corner_coordinates[0].tolist()
            if self.corner_coordinates[0][0][0] > 200:
                self.corner_coordinates.clear()
                self.calibrate_board(cap)
        else:
            self.calibrate_board(cap)

    def capture_image(self, cap, valid_move):
        while 1:
            ret, frame = cap.read()
            grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            cv2.imshow('img1', grey)
            state = GPIO.input(37)

            if valid_move:
                GPIO.output(11, GPIO.LOW)
                GPIO.output(21, GPIO.HIGH)
            else:
                GPIO.output(11, GPIO.HIGH)
                GPIO.output(21, GPIO.LOW)

            if cv2.waitKey(30) & 0xFF == ord('c'):
                self.calibrate_board(cap)

            if state == False:  # Push button pressed by user
                print("Image captured!")
                time.sleep(.2)
                self.image_subtraction(grey, valid_move)
                break

    def image_subtraction(self, img_2, valid_move):
        x = 0
        y = 0
        img_2 = img_2[y:y + 440, x: x + 400]
        cv2.imwrite('/home/linaro/Pictures/c2.png', img_2)

        if valid_move:
            img_1 = cv2.imread('/home/linaro/Pictures/calibrated_board.png', cv2.IMREAD_GRAYSCALE)
        else:
            img_1 = cv2.imread('/home/linaro/Pictures/c1.png', cv2.IMREAD_GRAYSCALE)
        img_1 = img_1[y:y + 440, x: x + 400]
        cv2.imwrite('/home/linaro/Pictures/c1.png', img_1)

        img_sub = cv2.absdiff(img_1, img_2)
        cv2.imwrite('/home/linaro/Pictures/diff.png', img_sub)
        cv2.imwrite('/home/linaro/Pictures/calibrated_board.png', img_2)

    def process_image(self):
        img_sub = cv2.imread('/home/linaro/Pictures/diff.png')
        grey = cv2.cvtColor(img_sub, cv2.COLOR_BGR2GRAY)
        grey = cv2.GaussianBlur(grey, (9, 9), 0)  # (9,9) = size of the kernel
        predicted_circles = cv2.HoughCircles(grey, cv2.HOUGH_GRADIENT, dp=1, minDist=15,
                                             param1=30, param2=15, minRadius=10, maxRadius=20)

        if predicted_circles is not None:
            print(predicted_circles.shape[1])
            print("Circles found")
            predicted_circles = np.round(predicted_circles[0, :]).astype("int")
            for (x, y, r,) in predicted_circles:
                cv2.circle(img_sub, (x, y), r, (0, 255, 0), 1)
                cv2.rectangle(img_sub, (x - 1, y - 1), (x + 1, y + 1), (0, 0, 255), -1)

        ##        cv2.imshow("output",img_sub)
        cv2.imwrite('/home/linaro/Pictures/circles_detected.png', img_sub)
        ##        cv2.waitKey()
        cv2.destroyAllWindows()
        print(predicted_circles)
        return predicted_circles

    def calculate_coordinates(self, circle_coordinates):
        predicted_squares = []
        print("First coordinate: ", self.corner_coordinates[0][0])
        square_width = self.corner_coordinates[1][0][0] - self.corner_coordinates[0][0][0]
        square_height = self.corner_coordinates[7][0][1] - self.corner_coordinates[5][0][1]
        board_offset = [self.corner_coordinates[0][0][0] - square_width,
                        self.corner_coordinates[0][0][1] - square_height]
        print("Square width: ", square_width)
        print("Square height: ", square_height)
        print("First coordinate: ", self.corner_coordinates[0][0])
        print("Board offset: ", board_offset)

        for coordinates in circle_coordinates:
            row = math.floor((coordinates[0] - board_offset[0]) / square_width)
            col = math.floor((coordinates[1] - board_offset[1]) / square_height)
            predicted_squares.append([col, row])

        print(predicted_squares)
        return predicted_squares