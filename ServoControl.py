#! /usr/bin/python3
import serial
import crcmod
import ASUS.GPIO as GPIO
import time
from Registers import Registers
import struct
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np


class ServoControl(object):
    def __init__(self):
        self.baud_rate = 1000000
        self.direction_pin = 12
        self.wrist_pin = 23
        self.wrist_pwm = None
        self.gripper_pin = 21
        self.gripper_pwm = None
        self.serial_port = '/dev/ttyS1'
        self.timeout = 0.05
        self.serial_connection = None
        self.ping = 0x01
        self.read = 0x02
        self.write = 0x03
        self.sync_read = 0x82
        self.sync_write = 0x83
        self.bulk_read = 0x92
        self.bulk_write = 0x93
        self.sync_id = 0xFE
        self.broadcast_id = 0xFE
        self.x_axis_data = [0]
        self.y_axis_data = [0]
        self.live_plot = plt.figure()
        self.ax1 = self.live_plot.add_subplot(1, 1, 1)
        self.start_time = 0
        self.servo_ids = [1, 2, 3, 4]
        self.goal_positions = []

    def pin_setup(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.direction_pin, GPIO.OUT)
        GPIO.setup(self.gripper_pin, GPIO.OUT)
        GPIO.setup(self.wrist_pin, GPIO.OUT)
        GPIO.output(self.gripper_pin, GPIO.HIGH)
        GPIO.output(self.wrist_pin, GPIO.HIGH)
        self.gripper_pwm = GPIO.PWM(self.gripper_pin, 61.3)
        self.wrist_pwm = GPIO.PWM(self.wrist_pin, 61.3)
        self.gripper_pwm.start(9)
        self.wrist_pwm.start(self.wrist_duty_cycle(135))
        GPIO.setwarnings(False)

    def serial_setup(self):
        try:
            self.serial_connection = serial.Serial(self.serial_port, self.baud_rate, timeout=self.timeout)
        except serial.SerialException:
            raise IOError("Error connecting to Servomotors")

    def generate_packet(self, servo_id, instruction, packet_parameters):
        parameter_count = len(packet_parameters)
        packet_length = parameter_count + 3
        packet = [0xff, 0xff, 0xfd, 0x00, servo_id, packet_length, 0, instruction]
        for parameter in packet_parameters:
            packet.append(parameter)
        packet = bytearray(packet)
        self.calculate_crc(packet)
        return packet

    @staticmethod
    def calculate_crc(packet):
        crc_fun = crcmod.mkCrcFun(0x18005, initCrc=0, rev=False)  # Calculate CRC1 and CRC2
        crc = crc_fun(bytes(packet))  # Convert binary value to byte_count
        packet.extend(struct.pack('<H', crc))

    @staticmethod
    def calculate_parameters(command, position):
        r = Registers()
        address = r.get_address(command)
        print("Address:", address)
        byte_count = r.get_bytes(command)
        print("Byte count: ", byte_count)
        parameter_1 = address  # Low-order byte from the starting address
        parameter_2 = 0x00  # High-order byte from the starting address
        if position == 1:
            parameter_3 = 0x01  # Turn on
        else:
            parameter_3 = 0x00  # Turn off

        if position == 3:
            parameter_3 = 0x03

        if position == -1:
            parameter_3 = byte_count
            parameter_4 = 0x00
            parameters = [parameter_1, parameter_2, parameter_3, parameter_4]
            return parameters

        if byte_count > 2:
            if position == -1:
                parameter_3 = byte_count  # Low-order byte from the data length (X)
                parameter_4 = 0  # High-order byte from the data length (X)
                parameters = [parameter_1, parameter_2, parameter_3, parameter_4]
            else:
                desired_value = hex(position)[2:].zfill(byte_count * 2)
                parameter_3 = int(desired_value[6:8], 16)  # First Byte
                parameter_4 = int(desired_value[4:6], 16)  # Second Byte
                parameter_5 = int(desired_value[2:4], 16)  # Third Byte
                parameter_6 = int(desired_value[:2], 16)  # Forth Byte
                parameters = [parameter_1, parameter_2, parameter_3, parameter_4, parameter_5, parameter_6]
        else:
            if address == 84 or address == 82 or address == 80:
                desired_value = hex(position)[2:].zfill(byte_count * 2)
                parameter_3 = int(desired_value[2:4], 16)  # First Byte
                parameter_4 = int(desired_value[:2], 16)  # Second Byte
                parameters = [parameter_1, parameter_2, parameter_3, parameter_4]
            else:
                parameters = [parameter_1, parameter_2, parameter_3]
        return parameters

    def get_write_sync_parameters(self, command):
        r = Registers()
        address = r.get_address(command)
        byte_count = r.get_bytes(command)
        parameters = []
        parameters.append(address)  # Low-order byte from the starting address
        parameters.append(0x00)  # High-order byte from the starting address
        parameters.append(byte_count)
        parameters.append(0x00)
        for servo, position in zip(self.servo_ids, self.goal_positions):
            parameters.append(servo)  # Servo ID
            desired_value = hex(position)[2:].zfill(byte_count * 2)  # Goal position
            parameters.append(int(desired_value[6:8], 16))  # First Byte
            parameters.append(int(desired_value[4:6], 16))  # Second Byte
            parameters.append(int(desired_value[2:4], 16))  # Third Byte
            parameters.append(int(desired_value[:2], 16))  # Fourth Byte

        return parameters

    def get_read_sync_parameters(self, command):
        r = Registers()
        address = r.get_address(command)
        byte_count = r.get_bytes(command)
        parameters = []
        parameters.append(address)  # Low-order byte from the starting address
        parameters.append(0x00)  # High-order byte from the starting address
        parameters.append(byte_count)
        parameters.append(0x00)

        for servo in self.servo_ids:
            parameters.append(servo)  # Servo ID

        return parameters

    def transmit_packet(self, command, position, operation, servo_id):
        if operation == self.sync_write:  # Sync write
            parameters = self.get_write_sync_parameters(command)
        elif operation == self.sync_read:  # Sync Read
            parameters = self.get_read_sync_parameters(command)
        else:
            parameters = self.calculate_parameters(command, position)

        packet = self.generate_packet(servo_id, operation, parameters)
        try:
            GPIO.output(self.direction_pin, GPIO.HIGH)
            time.sleep(0.000001)
            self.serial_connection.flushInput()
            self.serial_connection.write(packet)
            time.sleep(0.0002)  # Time taken for bits to be sent to servo @ 1Mbps
            time.sleep(0.000001)
            GPIO.output(self.direction_pin, GPIO.LOW)
            time.sleep(0.1)  # Return time delay
#            for i in range(len(self.servo_ids)):
           # self.read_packet()
            self.serial_connection.flushInput()
        except:
            print("Error occurred")

    def read_packet(self):
        position = 0
        self.serial_connection.flushOutput()
        header = self.serial_connection.read(3)
        body = self.serial_connection.read(5)
        parameter_count = body[2] - 4
        error = self.serial_connection.read(1)
        print("Error: ", error)
        character_format = "<B"
        error_message = struct.unpack(character_format, error)[0]
        print(error_message)

        if parameter_count > 0:
            parameters = self.serial_connection.read(parameter_count)
            print(parameters)
            if parameter_count == 4:
                character_format = "<I"  # Reverse bytes (Little-endian) and store as unsigned integer
            if parameter_count == 2:
                character_format = "<H"  # Reverse bytes (Little-endian) and store as unsigned Short
            if parameter_count == 1:
                character_format = "<B"  # Reverse bytes (Little-endian) and store as unsigned char

            position = struct.unpack(character_format, parameters)[
                0]  # Reverse bytes (Little-endian) and store as unsigned integer
        crc_1 = self.serial_connection.read(1)
        crc_2 = self.serial_connection.read(1)
        ##        print("CRCs: ",crc_1, crc_2)
        #        print("Position: ", position)
        if position:
            print("Position: ", position)
        #            self.draw_graph(position)
        else:
            print("No Position")

    def draw_graph(self, position_reading):
        if len(self.y_axis_data) == 1:
            self.start_time = time.time()
        time_axis = time.time() - self.start_time
        self.x_axis_data.append(time_axis)
        if position_reading:
            self.y_axis_data.append(position_reading)
            if position_reading == 2615 or position_reading == 2048 \
                    or position_reading == 2607:
                print("Settling time: ", time_axis)
        else:
            self.y_axis_data.append(0)

        if len(self.x_axis_data) > 50:
            self.x_axis_data = self.x_axis_data[-50:]
            self.y_axis_data = self.y_axis_data[-50:]

    #        self.ax1.clear()
    #        self.ax1.plot(self.x_axis_data, self.y_axis_data)

    def terminate_serial(self):
        self.serial_connection.close()
        self.gripper_pwm.stop()
        self.wrist_pwm.stop()
        GPIO.cleanup()

    def get_reading(self, i):
        self.transmit_packet('Present Position', -1, self.read, self.servo_ids[1])
        # self.transmit_packet('Moving Status', -1, self.read, servo_id)

    def animate(self):
        animation.FuncAnimation(self.live_plot, self.get_reading, interval=1)
        plt.show()

    def initialise_servos(self):
        self.transmit_packet('LED', 1, self.write, self.broadcast_id)
        # V = 20, A = 5, 60 x 0.229 = 13.74 rpm
        self.transmit_packet('Profile Velocity', 40, self.write, self.broadcast_id)
        self.transmit_packet('Profile Acceleration', 20, self.write, self.broadcast_id)
        self.transmit_packet('Position P Gain', 640, self.write, self.broadcast_id)
        # D = 5000
        self.transmit_packet('Position D Gain', 4000, self.write, self.broadcast_id)
        # I = 2000
        self.transmit_packet('Position I Gain', 300, self.write, self.broadcast_id)
        # servos.transmit_packet('Feedforward 2nd Gain', 0, self.write, self.broadcast_id)
        # servos.transmit_packet('Feedforward 1st Gain', 0, self.write, self.broadcast_id)
        self.transmit_packet('Torque Enable', 1, self.write, self.broadcast_id)

    def set_servo_limits(self):
        self.transmit_packet('Torque Enable', 0, self.write, 3)
        self.transmit_packet('Max Position Limit', 3072, self.write, 3)
        self.transmit_packet('Min Position Limit', 2048, self.write, 3)
        self.transmit_packet('Torque Enable', 0, self.write, 2)
        self.transmit_packet('Max Position Limit', 2048, self.write, 2)
        self.transmit_packet('Min Position Limit', 1024, self.write, 2)

    def learn_positions(self):
        self.transmit_packet('Torque Enable', 0, self.write, self.broadcast_id)

        while 1:
            print("WAIST SERVO")
            self.transmit_packet('Present Position', -1, self.read, 1)
            print("SHOULDER SERVO 1")
            self.transmit_packet('Present Position', -1, self.read, 2)
            print("SHOULDER SERVO 2")
            self.transmit_packet('Present Position', -1, self.read, 3)
            print("ELBOW SERVO")
            self.transmit_packet('Present Position', -1, self.read, 4)
            time.sleep(10)

    @staticmethod
    def wrist_duty_cycle(wrist_angle):
        return (0.0625 * wrist_angle) + 2.95

    def actuate_wrist(self, angle):
        self.wrist_pwm.ChangeDutyCycle(self.wrist_duty_cycle(angle))

    def gripper_suction(self):
        self.gripper_pwm.ChangeDutyCycle(7.603)

    def gripper_blow(self):
        self.gripper_pwm.ChangeDutyCycle(10.644)

    def ik_calculations(self):
        x = 83.125
        y = 264.375
        humerus_length = 210
        radius_length = 165
        waist_angle = self.calculate_waist_angle(x, y)
        extension_distance = self.calculate_extension_distance(x, y)
        print(extension_distance)
        shoulder_angle = self.calculate_angle(humerus_length, extension_distance, radius_length)
        elbow_angle = self.calculate_angle(humerus_length, radius_length, extension_distance)
        wrist_angle = 90-(180 - shoulder_angle - elbow_angle)
        print("Waist angle: ", waist_angle)
        print("Shoulder angle: ", shoulder_angle)
        print("Elbow angle: ", elbow_angle)
        print("Wrist angle: ", wrist_angle)
        waist_steps = self.angle_to_steps(waist_angle)*2
        shoulder_steps = self.angle_to_steps(shoulder_angle)
        waist_target = waist_steps+2048
        shoulder_1_target = 2048 - shoulder_steps
        shoulder_2_target = shoulder_steps+2048
        elbow_steps = self.angle_to_steps(elbow_angle)
        elbow_target = 2048 - elbow_steps
        print("Waist target: ", waist_target)
        print("Shoulder 1 target: ", shoulder_1_target)
        print("Shoulder 2 target: ", shoulder_2_target)
        print("Elbow target: ", elbow_target)

    @staticmethod
    def calculate_waist_angle(x_coordinate, y_coordinate):
        return np.rad2deg(np.arctan(x_coordinate/y_coordinate))

    @staticmethod
    def calculate_extension_distance(x, y):
        return np.sqrt(x**2 + y**2)

    @staticmethod
    def calculate_angle(adjacent_side_1, adjacent_side_2, opposite_side):
        return np.rad2deg(np.arccos((adjacent_side_1**2 + adjacent_side_2**2 - opposite_side**2) / (2*adjacent_side_1*adjacent_side_2)))

    @staticmethod
    def angle_to_steps(angle):
        resolution = 360./4096.
        step_size = 1./resolution
        return angle*step_size

    def calculate_square_coordinates(self, ):

    def actuate_robot_arm(self):
        self.gripper_blow()
        while 1:
            self.goal_positions = [2107, 2048, 2048, 2048]
            self.transmit_packet('Goal Position', 2048, self.sync_write, self.sync_id)
            self.actuate_wrist(180)
            time.sleep(5)
            self.goal_positions = [2467, 1656, 2411, 952]
            self.transmit_packet('Goal Position', 2048, self.sync_write, self.sync_id)
            self.actuate_wrist(45)
            time.sleep(2)
            self.goal_positions = [2467, 1605, 2520, 952]
            self.transmit_packet('Goal Position', 2048, self.sync_write, self.sync_id)
            time.sleep(4)
            self.gripper_suction()
            self.goal_positions = [2467, 1656, 2411, 1047]
            self.transmit_packet('Goal Position', 2048, self.sync_write, self.sync_id)
            time.sleep(2)
            self.goal_positions = [2335, 1588, 2501, 1034]
            self.transmit_packet('Goal Position', 2048, self.sync_write, self.sync_id)
            self.actuate_wrist(50)
            time.sleep(5)
            self.gripper_blow()
            time.sleep(3)
            self.goal_positions = [2335, 1656, 2411, 1034]
            self.transmit_packet('Goal Position', 2048, self.sync_write, self.sync_id)
            time.sleep(2)


if __name__ == '__main__':
    servos = ServoControl()
    servos.pin_setup()
    servos.serial_setup()
    servos.initialise_servos()
    # servos.set_servo_limits()
    # servos.learn_positions()
    servos.actuate_robot_arm()
    servos.terminate_serial()
