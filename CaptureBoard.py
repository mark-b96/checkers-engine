import numpy as np
import cv2
import math


class CaptureBoard(object):
    def __init__(self):
        self.cap = None

    def initialise_camera(self):
        cv2.setNumThreads(4)
        faceCascade = cv2.CascadeClassifier("/usr/local/share/OpenCV/haarcascades//haarcascade_frontalface_alt.xml")
        self.cap = cv2.VideoCapture("rkcamsrc io-mode=4 isp-mode=2A tuning-xml-path=/etc/cam_iq/IMX219.xml ! video/x-raw,format=NV12,width=640,height=480 ! videoconvert ! appsink")

    def calibrate_board(self):
        corner_coordinates = []  # 2D points on checkerboard
        ret, frame = self.cap.read()
        grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(grey, (7, 7), None)
        if ret:
            print("HERE")
            corner_coordinates.append(corners)
            img_grid = cv2.drawChessboardCorners(grey, (7, 7), corners, ret)
            cv2.imwrite('/home/linaro/Pictures/corners.png', img_grid)
        return corner_coordinates

    def capture_image(self):
        while 1:
            ret, frame = self.cap.read()
            grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            cv2.imshow('img1', grey)

            if cv2.waitKey(30) & 0xFF == ord('q'):
                print("First image captured!")
                img_1 = grey
                cv2.imwrite('/home/linaro/Pictures/c1.png', img_1)
            if cv2.waitKey(30) & 0xFF == ord('w'):
                print("Second image captured!")
                img_2 = grey
                cv2.imwrite('/home/linaro/Pictures/c2.png', img_2)
                img_sub = cv2.absdiff(img_1, img_2)
                cv2.imwrite('/home/linaro/Pictures/diff.png', img_sub)
                break

    def process_image(self):
        x = 0
        y = 0
        img1 = cv2.imread('/home/linaro/Pictures/c1.png')
        img2 = cv2.imread('/home/linaro/Pictures/c2.png')
        img_sub = cv2.absdiff(img1, img2)
        img_sub = img_sub[y:y + 350, x: x + 450]
        grey = cv2.cvtColor(img_sub, cv2.COLOR_BGR2GRAY)
        cv2.imshow("input", grey)
        cv2.waitKey()
        circles = cv2.HoughCircles(grey, cv2.HOUGH_GRADIENT, dp=1, minDist=15,
                                   param1=30, param2=15, minRadius=14, maxRadius=18)
        if circles is not None:
            print("Circles found")
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, r,) in circles:
                cv2.circle(img_sub, (x, y), r, (0, 255, 0), 1)
                cv2.rectangle(img_sub, (x - 1, y - 1), (x + 1, y + 1), (0, 0, 255), -1)

        cv2.imshow("output", img_sub)
        cv2.imwrite('/home/linaro/Pictures/circles_detected.png', img_sub)
        cv2.waitKey()
        print(circles)
        return circles

    def calculate_coordinates(self, corner_coordinates, circle_coordinates):
        predicted_squares = []
        corner_coordinates = corner_coordinates.tolist()
        square_width = corner_coordinates[1][0][0] - corner_coordinates[0][0][0]  # Width of square
        square_height = corner_coordinates[7][0][1] - corner_coordinates[5][0][1]  # Height of square
        offset = [corner_coordinates[0][0][0] - square_width, corner_coordinates[0][0][1] - square_height]  # Board offset
        print("Square width: ", square_width)
        print("Square height: ", square_height)
        print("First coordinate: ", corner_coordinates[0][0])
        print("Board offset: ", offset)

        for coordinates in circle_coordinates:
            row = math.floor((coordinates[0] - offset[0]) / square_width)
            col = math.floor((coordinates[1] - offset[1]) / square_height)
            predicted_squares.append([col, row])

        print(predicted_squares)
        return predicted_squares
