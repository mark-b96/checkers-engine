import numpy as np
import sys, os, cv2
from collections import Counter


def initialise_camera():
    cv2.setNumThreads(4)
    faceCascade = cv2.CascadeClassifier("/usr/local/share/OpenCV/haarcascades//haarcascade_frontalface_alt.xml")
    cap = cv2.VideoCapture("rkcamsrc io-mode=4 isp-mode=2A tuning-xml-path=/etc/cam_iq/IMX219.xml ! video/x-raw,format=NV12,width=640,height=480 ! videoconvert ! appsink")
    return cap

def capture_image(cap):
    while(True):
        ret, frame = cap.read()
        grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow('img1', grey)

        objpoints = []  # 3D points
        imgpoints = []  # 2D points
        x=0
        y=0

        if cv2.waitKey(30) & 0xFF == ord('q'):
            print("First image captured!")
            img1 = grey
            cv2.imwrite('/home/linaro/Pictures/c1.png', grey)
        if cv2.waitKey(30) & 0xFF == ord('w'):
            print("Second image captured!")
            img2 = grey
            cv2.imwrite('/home/linaro/Pictures/c2.png', grey)
            img_sub = cv2.absdiff(img1, img2)
            cv2.imwrite('/home/linaro/Pictures/diff.png', img_sub)
            ret, corners = cv2.findChessboardCorners(grey, (7,7), None)
            if ret:
                imgpoints.append(corners)
                img_grid = cv2.drawChessboardCorners(grey, (7,7), corners, ret)
                img_grid = img_grid[y: y+ 400, x:x +400]
                cv2.imwrite('/home/linaro/Pictures/corners.png', img_grid)
                cv2.imshow('img', grey)
            cap.release()
            break
    return imgpoints

def process_image():
    x=0
    y=0
    img1 = cv2.imread('/home/linaro/Pictures/c1.png')
    img2 = cv2.imread('/home/linaro/Pictures/c2.png')
    img_sub = cv2.absdiff(img1, img2)
    img_sub =  img_sub[y:y+ 330, x: x+270]
##    ret, thresh_1 = cv2.threshold(img_sub, 50, 255, cv2.THRESH_BINARY)
##    img_thresh = thresh_1
##    cv2.imwrite('/home/linaro/Pictures/threshold.png', thresh_1)
    grey = cv2.cvtColor(img_sub, cv2.COLOR_BGR2GRAY)
    circles = cv2.HoughCircles(grey, cv2.HOUGH_GRADIENT, dp=1,minDist=15,
                               param1=30, param2=15, minRadius=10, maxRadius=15)
    if circles is not None:
        print("Circles found")
        circles = np.round(circles[0, :]).astype("int")
        for (x,y,r,) in circles:
            cv2.circle(img_sub, (x,y),r, (0,255,0), 1)
            cv2.rectangle(img_sub, (x-1, y-1), (x+1, y+1), (0, 0,255),-1)

    cv2.imshow("output", img_sub)
    cv2.waitKey()
    print(circles)
    return circles
##    nonzero = cv2.findNonZero(grey)
##    cv2.destroyAllWindows()
##    return nonzero

def calculate_coordinates(corner_coordinates, circle_coordinates):
    checkers_board = np.full((8,8),list)
    corner_coordinates = corner_coordinates.tolist()
    square_size = corner_coordinates[1][0][0] - corner_coordinates[0][0][0]
    print("Initial square size: ", square_size)
    print("First corner: ", corner_coordinates[0], "Second corner: ", corner_coordinates[1])
    if square_size < 20:
        corner_coordinates[0] = corner_coordinates[-1]
        corner_coordinates[1] = corner_coordinates[-2]
        square_size = corner_coordinates[1][0][0] - corner_coordinates[0][0][0]
    offset = [corner_coordinates[0][0][0] -square_size, corner_coordinates[0][0][1]-square_size]
    print(square_size)
    print(offset)
    predicted_squares = []
    
    for row in range(8):
        for column in range(8):
            checkers_board[row][column] = [column*square_size +offset[0], row*square_size + offset[1]]     

    for row in range(8):
        for column in range(8):
            if row == 7:
                y_upper_bound = (1+row)*square_size +offset[1]
            else:
                y_upper_bound = checkers_board[row+1][column][1]
            if column == 7:
                x_upper_bound = (1+column)*square_size +offset[0]
            else:
                x_upper_bound = checkers_board[row][column+1][0]
            print(x_upper_bound, y_upper_bound)
            for coordinates in circle_coordinates:
                if checkers_board[row][column][0] < coordinates[0] < x_upper_bound and\
                   checkers_board[row][column][1] < coordinates[1] < y_upper_bound:
                    predicted_squares.append([row, column])
    
    counter = Counter(tuple(item) for item in predicted_squares)
    print(counter)
    
corner_coordinates = capture_image(initialise_camera())
process_image()
calculate_coordinates(corner_coordinates[0],process_image())
