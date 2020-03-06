"""
Author: Mark Bonney

"""
import numpy as np


class IKCalculations(object):
    def ik_calculations(self, square_row, square_column):
        x, y = self.calculate_square_coordinates(square_row, square_column)
##        if square_row < 4:
##            humerus_length = 235
####        elif square_row < 6:
####            humerus_length = 230
##        else:
##            humerus_length = 205 #210
##        radius_length = 190
        radius_length = 160
        humerus_length = 205
        waist_angle = self.calculate_waist_angle(x, y)
        extension_distance = self.calculate_extension_distance(x, y)
        shoulder_angle = 90 - self.calculate_angle(humerus_length, extension_distance, radius_length)
        elbow_angle = 180-self.calculate_angle(humerus_length, radius_length, extension_distance)
        wrist_angle = (180 - shoulder_angle - elbow_angle)
        waist_steps = self.angle_to_steps(waist_angle)*2  # For the 2:1 gear reduction
        shoulder_steps = self.angle_to_steps(shoulder_angle)
        if square_column < 4:
            waist_target = int(1885-waist_steps)
        else:
            waist_target = int(waist_steps+1885)
        shoulder_steps = shoulder_steps-175
        shoulder_1_target = int(2048 - shoulder_steps)
        shoulder_2_target = int(shoulder_steps+2048)
        elbow_steps = self.angle_to_steps(elbow_angle)
        elbow_target = int(2048 - elbow_steps)
        return [waist_target, shoulder_1_target, shoulder_2_target, elbow_target, wrist_angle]

    @staticmethod
    def calculate_waist_angle(x_coordinate, y_coordinate):
        return np.rad2deg(np.arctan(x_coordinate/y_coordinate))

    @staticmethod
    def calculate_extension_distance(x, y):
        return np.sqrt(x**2 + y**2)

    @staticmethod
    def calculate_angle(adjacent_side_1, adjacent_side_2, opposite_side):
        return np.rad2deg(np.arccos((adjacent_side_1**2 + adjacent_side_2**2 - opposite_side**2) /
                                    (2*adjacent_side_1*adjacent_side_2)))

    @staticmethod
    def angle_to_steps(angle):
        resolution = 360./4096.
        step_size = 1./resolution
        return angle*step_size

    @staticmethod
    def calculate_square_coordinates(row, column):
        square_size = 192./8.  # Size of square in mm
        board_distance = 105.0  # Distance from arm to board in mm, 105
        if column == 4:
            x_coordinate = square_size/4. +5.
        if column == 3:
            x_coordinate = square_size/4. + 5.
        if column < 3:
            x_coordinate = abs(((3-column)*square_size) + (square_size/4.))
        if column > 4:
            x_coordinate = ((column-4)*square_size) + (square_size/4.)
        y_coordinate = (row*square_size) + (square_size/2.) + board_distance
        return x_coordinate, y_coordinate
