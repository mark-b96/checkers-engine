"""
Author: Mark Bonney
"""


class Registers(object):
    def __init__(self):
        self.registers = {
                         'Model Number': [0, 2],
                         'Model Information': [2, 4],
                         'Firmware Version': [6, 1],
                         'ID': [7, 1],
                         'Baud Rate': [8, 1],
                         'Return Delay Time': [9, 1],
                         'Drive Mode': [10, 1],
                         'Operating Mode': [11, 1],
                         'Secondary(Shadow) ID': [12, 1],
                         'Protocol Type': [13, 1],
                         'Homing Offset': [20, 4],
                         'Moving Threshold': [24, 4],
                         'Temperature Limit': [31, 1],
                         'Max Voltage Limit': [32, 2],
                         'Min Voltage Limit': [34, 2],
                         'PWM Limit': [36, 2],
                         'Velocity Limit': [44, 4],
                         'Max Position Limit': [48, 4],
                         'Min Position Limit': [52, 4],
                         'Shutdown': [63, 1],
                         'Torque Enable': [64, 1],
                         'LED': [65, 1],
                         'Status Return Level': [68, 1],
                         'Registered Instruction': [69, 1],
                         'Hardware Error Status': [70, 1],
                         'Velocity I Gain': [76, 2],
                         'Velocity P Gain': [78, 2],
                         'Position D Gain': [80, 2],
                         'Position I Gain': [82, 2],
                         'Position P Gain': [84, 2],
                         'Feedforward 2nd Gain': [88, 4],
                         'Feedforward 1st Gain': [90, 4],
                         'Bus Watchdog': [98, 1],
                         'Goal PWM': [100, 2],
                         'Goal Velocity ': [104, 4],
                         'Profile Acceleration': [108, 4],
                         'Profile Velocity': [112, 4],
                         'Goal Position': [116, 4],
                         'Realtime Tick': [120, 2],
                         'Moving': [122, 1],
                         'Moving Status': [123, 1],
                         'Present PWM': [124, 2],
                         'Present Load': [126, 2],
                         'Present Velocity': [128, 4],
                         'Present Position': [132, 4],
                         'Velocity Trajectory': [136, 4],
                         'Position Trajectory': [140, 4],
                         'Present Input Voltage': [144, 2],
                         'Present Temperature': [146, 1]}

    def get_address(self, name):
        return self.registers[name][0]

    def get_bytes(self, name):
        return self.registers[name][1]