import numpy as np
import cv2
import math


class CaptureBoard(object):
    def __init__(self):
        self.corner_coordinates = []

    def initialise_camera(self):
        cv2.setNumThreads(4)
        faceCascade = cv2.CascadeClassifier("/usr/local/share/OpenCV/haarcascades//haarcascade_frontalface_alt.xml")
        cap = cv2.VideoCapture(
            "rkcamsrc io-mode=4 isp-mode=2A tuning-xml-path=/etc/cam_iq/IMX219.xml ! video/x-raw,format=NV12,width=640,height=480 ! videoconvert ! appsink")
        return cap

    def calibrate_board(self, cap):
        ret, frame = cap.read()
        grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        img_cal = grey
        cv2.imwrite('/home/linaro/Pictures/calibrated_board.png', img_cal)
        ret, corners = cv2.findChessboardCorners(grey, (7, 7), None)
        print("Attempting to calibrate board")
        if ret:
            print("HERE")
            self.corner_coordinates.append(corners)
            img_grid = cv2.drawChessboardCorners(grey, (7, 7), corners, ret)
            cv2.imwrite('/home/linaro/Pictures/corners.png', img_grid)
            self.corner_coordinates = self.corner_coordinates[0].tolist()
        else:
            self.calibrate_board(cap)

    def capture_image(self, cap):
        x = 0
        y = 0
        while 1:
            ret, frame = cap.read()
            grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            cv2.imshow('img1', grey)

            if cv2.waitKey(30) & 0xFF == ord('c'):
                self.calibrate_board(cap)

            if cv2.waitKey(30) & 0xFF == ord('q'):
                print("Image1 captured!")
                img_x = cv2.imread('/home/linaro/Pictures/calibrated_board.png')
                img_x = img_x[y:y + 400, x: x + 440]
                img_1 = cv2.cvtColor(img_x, cv2.COLOR_BGR2GRAY)
                cv2.imwrite('/home/linaro/Pictures/c1.png', img_1)

            if cv2.waitKey(30) & 0xFF == ord('w'):
                print("Image captured!")

                img_2 = grey
                img_2 = img_2[y:y + 400, x: x + 440]
                cv2.imwrite('/home/linaro/Pictures/c2.png', img_2)

                img_1 = cv2.imread('/home/linaro/Pictures/calibrated_board.png', cv2.IMREAD_GRAYSCALE)
                img_1 = img_1[y:y + 400, x: x + 440]
                cv2.imwrite('/home/linaro/Pictures/c1.png', img_1)

                img_sub = cv2.absdiff(img_1, img_2)
                cv2.imwrite('/home/linaro/Pictures/diff.png', img_sub)
                cv2.imwrite('/home/linaro/Pictures/calibrated_board.png', img_2)
                break

    def process_image(self):
        img_sub = cv2.imread('/home/linaro/Pictures/diff.png')
        grey = cv2.cvtColor(img_sub, cv2.COLOR_BGR2GRAY)
        circles = cv2.HoughCircles(grey, cv2.HOUGH_GRADIENT, dp=1, minDist=15,
                                   param1=30, param2=15, minRadius=10, maxRadius=16)
        if circles is not None:
            print("Circles found")
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, r,) in circles:
                cv2.circle(img_sub, (x, y), r, (0, 255, 0), 1)
                cv2.rectangle(img_sub, (x - 1, y - 1), (x + 1, y + 1), (0, 0, 255), -1)

        cv2.imshow("output", img_sub)
        cv2.imwrite('/home/linaro/Pictures/circles_detected.png', img_sub)
        cv2.waitKey()
        cv2.destroyAllWindows()
        print(circles)
        return circles

    def calculate_coordinates(self, circle_coordinates):
        predicted_squares = []
        print("First coordinate: ", self.corner_coordinates[0][0])
        square_width = self.corner_coordinates[1][0][0] - self.corner_coordinates[0][0][0]  # Width of square
        square_height = self.corner_coordinates[7][0][1] - self.corner_coordinates[5][0][1]  # Height of square
        offset = [self.corner_coordinates[0][0][0] - square_width,
                  self.corner_coordinates[0][0][1] - square_height]  # Board offset
        print("Square width: ", square_width)
        print("Square height: ", square_height)
        print("First coordinate: ", self.corner_coordinates[0][0])
        print("Board offset: ", offset)

        for coordinates in circle_coordinates:
            row = math.floor((coordinates[0] - offset[0]) / square_width)
            col = math.floor((coordinates[1] - offset[1]) / square_height)
            predicted_squares.append([col, row])

        print(predicted_squares)
        return predicted_squares