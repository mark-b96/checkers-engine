import serial
import crcmod
import ASUS.GPIO as GPIO
import time
from Registers import Registers
import struct
import matplotlib.pyplot as plt
import matplotlib.animation as animation


class ServoControl(object):
    def __init__(self):
        self.baud_rate = 1000000
        self.direction_pin = 12
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
        self.goal_positions = [2048, 2048, 2048, 2048]

    def pin_setup(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.direction_pin, GPIO.OUT)
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

    def get_sync_parameters(self, command):
        r = Registers()
        address = r.get_address(command)
        byte_count = r.get_bytes(command)
        parameters = []
        for servo, position in zip(self.servo_ids, self.goal_positions):
            parameters.append(address)  # Low-order byte from the starting address
            parameters.append(0x00)  # High-order byte from the starting address
            parameters.append(byte_count)
            parameters.append(0x00)
            parameters.append(servo)  # Servo ID
            desired_value = hex(position)[2:].zfill(byte_count * 2)  # Goal position
            parameters.append(int(desired_value[6:8], 16))  # First Byte
            parameters.append(int(desired_value[4:6], 16))  # Second Byte
            parameters.append(int(desired_value[2:4], 16))  # Third Byte
            parameters.append(int(desired_value[:2], 16))  # Fourth Byte

        return parameters

    def transmit_packet(self, command, position, operation, servo_id):
        if operation == 0x83:
            parameters = self.get_sync_parameters(command)
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
            self.read_packet()
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
        print("Position: ", position)
        if position:
            self.draw_graph(position)
        else:
            print("No Position")

    def draw_graph(self, position_reading):
        if len(self.y_axis_data) == 1:
            self.start_time = time.time()
        time_axis = time.time() - self.start_time
        self.x_axis_data.append(time_axis)
        if position_reading:
            self.y_axis_data.append(position_reading)
            if position_reading == 2694 or position_reading == 2048 \
                    or position_reading == 2607:
                print("Settling time: ", time_axis)
        else:
            self.y_axis_data.append(0)

        if len(self.x_axis_data) > 50:
            self.x_axis_data = self.x_axis_data[-50:]
            self.y_axis_data = self.y_axis_data[-50:]

        self.ax1.clear()
        self.ax1.plot(self.x_axis_data, self.y_axis_data)

    def terminate_serial(self):
        self.serial_connection.close()
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
        self.transmit_packet('Profile Velocity', 20, self.write, self.broadcast_id)
        self.transmit_packet('Profile Acceleration', 5, self.write, self.broadcast_id)
        self.transmit_packet('Position P Gain', 640, self.write, self.broadcast_id)
        # D = 5000
        self.transmit_packet('Position D Gain', 6000, self.write, self.broadcast_id)
        # I = 2000
        self.transmit_packet('Position I Gain', 2000, self.write, self.broadcast_id)
        # servos.transmit_packet('Feedforward 2nd Gain', 0, self.write, self.broadcast_id)
        # servos.transmit_packet('Feedforward 1st Gain', 0, self.write, self.broadcast_id)
        self.transmit_packet('Torque Enable', 1, self.write, self.broadcast_id)

    def set_servo_limits(self):
        self.transmit_packet('Torque Enable', 0, self.write, 2)
        self.transmit_packet('Max Position Limit', 3072, self.write, 2)
        self.transmit_packet('Min Position Limit', 2048, self.write, 2)
        self.transmit_packet('Torque Enable', 0, self.write, 3)
        self.transmit_packet('Max Position Limit', 2048, self.write, 3)
        self.transmit_packet('Min Position Limit', 1024, self.write, 3)

    def learn_positions(self):
        self.transmit_packet('Torque Enable', 0, self.write, self.broadcast_id)

        while 1:
            print("ELBOW SERVO")
            self.transmit_packet('Present Position', -1, self.read, 1)
            print("SHOULDER SERVO 1")
            self.transmit_packet('Present Position', -1, self.read, 2)
            print("SHOULDER SERVO 2")
            self.transmit_packet('Present Position', -1, self.read, 3)
            print("WAIST SERVO")
            self.transmit_packet('Present Position', -1, self.read, 4)
            time.sleep(10)

    def actuate_robot_arm(self):
        servos.initialise_servos()
        servos.transmit_packet('Goal Position', 2048, self.sync_write, self.sync_id)
        servos.animate()


if __name__ == '__main__':
    servos = ServoControl()
    servos.pin_setup()
    servos.serial_setup()
    servos.actuate_robot_arm()
    servos.terminate_serial()
