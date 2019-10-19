"""
Author: Mark Bonney
"""
import numpy as np
import cv2
import math
import ASUS.GPIO as GPIO
import time
import ast


class CaptureBoard(object):
    def __init__(self):
        self.corner_coordinates = []
        self.push_button_pin = 37
        self.red_led_pin = 33
        self.green_led_pin = 35

    def initialise_camera(self):
        cv2.setNumThreads(4)
        faceCascade = cv2.CascadeClassifier("/usr/local/share/OpenCV/haarcascades//haarcascade_frontalface_alt.xml")
        cap = cv2.VideoCapture(
            "rkcamsrc io-mode=4 isp-mode=2A tuning-xml-path=/etc/cam_iq/IMX219.xml ! video/x-raw,format=NV12,width=640,height=480 ! videoconvert ! appsink")
        return cap

    def pin_setup(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.push_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Push-button pin with pull-up resistor
        GPIO.setup(self.red_led_pin, GPIO.OUT)  # Red LED output
        GPIO.setup(self.green_led_pin, GPIO.OUT)  # Green LED output

    def start_game(self, cap):
        x = 0
        y = 0
        with open('calibration.txt', 'r') as f:
            for coordinate in f:
                self.corner_coordinates.append(coordinate.strip())
        self.corner_coordinates = [ast.literal_eval(i) for i in self.corner_coordinates]
        while 1:
            state_1 = GPIO.input(self.push_button_pin)
            if state_1 == False:
                time.sleep(0.2)
                ret, frame = cap.read()
                grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert image to greyscale
                img_init = grey
                img_init = img_init[y:y + 480, x: x + 400]
                cv2.imwrite('/home/linaro/Pictures/calibrated_board.png', img_init)
                print("Game commencing")
                break

    def calibrate_board(self, cap):
        x = 0
        y = 0
        self.corner_coordinates = []
        ret, frame = cap.read()
        grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert image to greyscale
        img_cal = grey
        img_cal = img_cal[y:y + 480, x: x + 400]
##        cv2.imwrite('/home/linaro/Pictures/calibrated_board.png', img_cal)
        ret, corners = cv2.findChessboardCorners(grey, (7, 7), None)
        print("Attempting to calibrate board")
        if ret:
            print("Board Located")
            self.corner_coordinates.append(corners)
            img_grid = cv2.drawChessboardCorners(img_cal, (7, 7), corners, ret)
            cv2.imwrite('/home/linaro/Pictures/corners.png', img_grid)
            self.corner_coordinates = self.corner_coordinates[0].tolist()
            if self.corner_coordinates[0][0][0] > 200:
                self.corner_coordinates.clear()
                print("Fail 1. Attempting to recalibrate")
                time.sleep(2)
                self.calibrate_board(cap)
            print("Board successfully calibrated")
            with open('calibration.txt', 'w') as f:
                for coordinate in self.corner_coordinates:
                    f.write("%s\n" % coordinate)
        else:
            print("Fail 2. Attempting to recalibrate")
            time.sleep(2)
            self.calibrate_board(cap)

    def capture_image(self, cap, valid_move, ai_move):
        while 1:
            ret, frame = cap.read()
            grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#            cv2.imshow('img1', grey)
            state_2 = GPIO.input(self.push_button_pin)

            if cv2.waitKey(30) & 0xFF == ord('c'):
                self.calibrate_board(cap)
                valid_move = True

            if valid_move:
                GPIO.output(self.red_led_pin, GPIO.LOW)
                GPIO.output(self.green_led_pin, GPIO.HIGH)
            else:
                GPIO.output(self.red_led_pin, GPIO.HIGH)
                GPIO.output(self.green_led_pin, GPIO.LOW)

            if state_2 == False or ai_move:  # Push button pressed by user/ robot's turn
                start_time = time.time()
                print("Image captured!")
                time.sleep(.2)
                elapsed_time = time.time() - start_time
                print(elapsed_time)
                self.image_subtraction(grey, valid_move)
                break

    def image_subtraction(self, img_2, valid_move):
        x = 0
        y = 0
        img_2 = img_2[y:y + 480, x: x + 400]
        cv2.imwrite('/home/linaro/Pictures/c2.png', img_2)

        if valid_move:
            img_1 = cv2.imread('/home/linaro/Pictures/calibrated_board.png', cv2.IMREAD_GRAYSCALE)
        else:
            img_1 = cv2.imread('/home/linaro/Pictures/c1.png', cv2.IMREAD_GRAYSCALE)
        img_1 = img_1[y:y + 480, x: x + 400]
        cv2.imwrite('/home/linaro/Pictures/c1.png', img_1)

        img_sub = cv2.absdiff(img_1, img_2)
        cv2.imwrite('/home/linaro/Pictures/diff.png', img_sub)
        cv2.imwrite('/home/linaro/Pictures/calibrated_board.png', img_2)

    def process_image(self):
        img_sub = cv2.imread('/home/linaro/Pictures/diff.png')
        grey = cv2.cvtColor(img_sub, cv2.COLOR_BGR2GRAY)
        grey = cv2.GaussianBlur(grey, (9, 9), 0)  # (9,9) = size of the kernel
        predicted_circles = cv2.HoughCircles(grey, cv2.HOUGH_GRADIENT, dp=1, minDist=20, # minDist = 16
                                             param1=30, param2=15, minRadius=10, maxRadius=20) #minradius = 10, 20

        if predicted_circles is not None or predicted_circles.shape[1] > 3 or\
            predicted_circles.shape[1] < 2:
            print(predicted_circles.shape[1])
            print("Circles found")
            sorted_circles = []
            updated_circles = []
            print("Predicted circles: ", predicted_circles[0])
            if predicted_circles.shape[1] == 3:
                for circle in predicted_circles[0]:
                    sorted_circles.append(circle[0])
                sorted_circles.sort()
                print("Sorted circles: ", sorted_circles)
                middle_piece = sorted_circles[1]
                print("Middle piece: ", middle_piece)
                for index, circle in enumerate(predicted_circles[0]):
                    if circle[0] == middle_piece:
                        print("Pre deletion: ", circle)
                        print("index: ", index)
                        updated_circles = np.delete(predicted_circles[0], index, 0)
                        predicted_circles = np.array([updated_circles])
                        print("New predicted circles: ", predicted_circles)
                        break
            predicted_circles = np.round(predicted_circles[0, :]).astype("int")
            for (x, y, r,) in predicted_circles:
                cv2.circle(img_sub, (x, y), r, (0, 255, 0), 1)
                cv2.rectangle(img_sub, (x - 1, y - 1), (x + 1, y + 1), (0, 0, 255), -1)

        cv2.imwrite('/home/linaro/Pictures/circles_detected.png', img_sub)
        cv2.destroyAllWindows()
        print(predicted_circles)
        return predicted_circles

    def calculate_coordinates(self, circle_coordinates):
        predicted_squares = []
        print("First coordinate: ", self.corner_coordinates[0][0])
        square_width = self.corner_coordinates[1][0][0] - self.corner_coordinates[0][0][0]
        square_height = self.corner_coordinates[13][0][1] - self.corner_coordinates[5][0][1]
        board_offset = [self.corner_coordinates[0][0][0] - square_width,
                        self.corner_coordinates[0][0][1] - square_height]
        angle_height = self.corner_coordinates[6][0][1] - self.corner_coordinates[0][0][1]
        print("Square width: ", square_width)
        print("Square height: ", square_height)
        print("First coordinate: ", self.corner_coordinates[0][0])
        print("Board offset: ", board_offset)

        for coordinates in circle_coordinates:
            row = math.floor((coordinates[0] - board_offset[0]) / square_width)
            col = math.floor((coordinates[1] - board_offset[1]- angle_height) / square_height)
            predicted_squares.append([col, row])

        print(predicted_squares)
        return predicted_squares