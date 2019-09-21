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
        self.x_axis_data = [0]
        self.y_axis_data = [0]
        self.live_plot = plt.figure()
        self.ax1 = self.live_plot.add_subplot(1, 1, 1)
        self.start_time = 0

    def pin_setup(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.direction_pin, GPIO.OUT)
        GPIO.setwarnings(False)

    def serial_setup(self):
        try:
            self.serial_connection = serial.Serial(self.serial_port, self.baud_rate, timeout=self.timeout)
        except:
            print("Error connecting to serial port")

    def generate_packet(self, servo_id, instruction, packet_parameters):
        parameter_count = len(packet_parameters)
        packet_length = parameter_count + 3
        packet = [0xff, 0xff, 0xfd, 0x00, servo_id, packet_length, 0, instruction]
        for parameter in packet_parameters:
            packet.append(parameter)
        packet = bytearray(packet)
        self.calculate_crc(packet)
        return packet

    def calculate_crc(self, packet):
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
            parameter_3 = 0x03  # Baud Rate = 1000000

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
                ##                print("Desired value: ", desired_value)
                parameter_3 = int(desired_value[6:8], 16)  # First Byte
                parameter_4 = int(desired_value[4:6], 16)  # Second Byte
                parameter_5 = int(desired_value[2:4], 16)  # Third Byte
                parameter_6 = int(desired_value[:2], 16)  # Forth Byte
                parameters = [parameter_1, parameter_2, parameter_3, parameter_4, parameter_5, parameter_6]
        else:
            if address == 84 or address == 82 or address == 80:
                desired_value = hex(position)[2:].zfill(byte_count * 2)
                ##                print(desired_value)
                parameter_3 = int(desired_value[2:4], 16)  # First Byte
                ##                print("Parameter3: ", parameter_3)
                parameter_4 = int(desired_value[:2], 16)  # Second Byte
                ##                print("Parameter4: ", parameter_4)
                parameters = [parameter_1, parameter_2, parameter_3, parameter_4]
            else:
                parameters = [parameter_1, parameter_2, parameter_3]
        return parameters

    @staticmethod
    def get_sync_parameters(command, id_1, id_2, pos_1, pos_2):
        r = Registers()
        address = r.get_address(command)
        byte_count = r.get_bytes(command)
        parameter_1 = address  # Low-order byte from the starting address
        parameter_2 = 0x00  # High-order byte from the starting address
        parameter_3 = byte_count
        parameter_4 = 0x00
        parameter_5 = id_1
        desired_value = hex(pos_1)[2:].zfill(byte_count * 2)
        parameter_6 = int(desired_value[6:8], 16)  # First Byte
        parameter_7 = int(desired_value[4:6], 16)  # Second Byte
        parameter_8 = int(desired_value[2:4], 16)  # Third Byte
        parameter_9 = int(desired_value[:2], 16)  # Forth Byte
        parameter_10 = id_2
        desired_value = hex(pos_2)[2:].zfill(byte_count * 2)
        parameter_11 = int(desired_value[6:8], 16)  # First Byte
        parameter_12 = int(desired_value[4:6], 16)  # Second Byte
        parameter_13 = int(desired_value[2:4], 16)  # Third Byte
        parameter_14 = int(desired_value[:2], 16)  # Forth Byte

        parameters = [parameter_1, parameter_2, parameter_3, parameter_4,
                      parameter_5, parameter_6, parameter_7, parameter_8,
                      parameter_9, parameter_10, parameter_11, parameter_12,
                      parameter_13, parameter_14]
        return parameters

    def transmit_packet(self, command, position, operation, servo_id):
        if operation == 0x83:
            ##            parameters = self.get_sync_parameters(command, 2, 3,2613, 1512)
            ##            parameters = self.get_sync_parameters(command, 2, 3,2506, 1578)
            parameters = self.get_sync_parameters(command, 2, 3, 2048, 2048)
        ##            parameters = self.get_sync_parameters(command, 2, 3,2694, 1421)
        ##            parameters = self.get_sync_parameters(command, 2, 3,2607, 1482)
        else:
            parameters = self.calculate_parameters(command, position)

        packet = self.generate_packet(servo_id, operation, parameters)
        try:
            GPIO.output(self.direction_pin, GPIO.HIGH)
            time.sleep(0.000001)
            self.serial_connection.flushInput()
            self.serial_connection.write(packet)
            ##            print("Sending Packet")
            time.sleep(0.0002)  # Time taken for bits to be sent to servo @ 1Mbps
            time.sleep(0.000001)
            GPIO.output(self.direction_pin, GPIO.LOW)
            time.sleep(0.1)  # Return time delay
            ##            print("Receiving Packet")
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
                character_format = "<I"  # Reverse bytes (Little-edian) and store as unsigned integer
            if parameter_count == 2:
                character_format = "<H"  # Reverse bytes (Little-edian) and store as unsigned Short
            if parameter_count == 1:
                character_format = "<B"  # Reverse bytes (Little-edian) and store as unsigned char

            position = struct.unpack(character_format, parameters)[
                0]  # Reverse bytes (Little-edian) and store as unsigned integer
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
        ##        print(time_axis)
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
        ping = 0x01
        read = 0x02
        write = 0x03
        reboot = 0x08
        clear = 0x10
        servo_id = 2
        self.transmit_packet('Present Position', -1, read, servo_id)

    ##        self.transmit_packet('Moving Status', -1, read, servo_id)
    ##        self.transmit_packet('Moving Status', -1, read, servo_id)
    ##        servos.transmit_packet('Goal Position',  1140, write, 2)

    def animate(self):
        ani = animation.FuncAnimation(self.live_plot, self.get_reading, interval=1)
        plt.show()


if __name__ == '__main__':
    ping = 0x01
    read = 0x02
    write = 0x03
    reboot = 0x08
    clear = 0x10
    sync_write = 131
    servo_id = 3
    sync_id = 0xFE
    # Servo_1_Limits: 1536(left), 1024 (mid), 512(right)
    # Servo_2_Limits: 3072(left), 2048 (mid), 1536(right)
    ids = [1, 2, 3, 4]
    servos = ServoControl()
    servos.pin_setup()
    servos.serial_setup()
    ##    servos.transmit_packet('Torque Enable', 0, write, 2)
    ##    servos.transmit_packet('Max Position Limit',3072, write, 2)
    ##    servos.transmit_packet('Min Position Limit',2048, write, 2)
    ##    servos.transmit_packet('Torque Enable', 0, write, 3)
    ##    servos.transmit_packet('Max Position Limit',2048, write, 3)
    ##    servos.transmit_packet('Min Position Limit',1024, write, 3)
    ##    for servo_id in ids:
    ##        servos.transmit_packet('LED', 1, write, servo_id)
    ##        # V = 20, A = 5
    ##        servos.transmit_packet('Profile Velocity', 20, write, servo_id) # 60 x 0.229 = 13.74 rpm
    ##        servos.transmit_packet('Profile Acceleration', 5, write, servo_id) # 10
    ##        servos.transmit_packet('Position P Gain', 640, write, servo_id) # 640    -> K/128   Kp = 5   1500/5 = 300    1500
    ##        # D = 5000
    ##        servos.transmit_packet('Position D Gain', 6000, write, servo_id) # 4000  -> K/16    Kd = 375                 25000
    ##        # I = 2000
    ##        servos.transmit_packet('Position I Gain', 2000, write, servo_id) # 75  -> K/65536     Ki = 0.001               50
    ####        servos.transmit_packet('Feedforward 2nd Gain', 0, write, servo_id)
    ####        servos.transmit_packet('Feedforward 1st Gain', 0, write, servo_id)
    ##        servos.transmit_packet('Torque Enable', 1, write, servo_id)

    ##    servos.transmit_packet('Feedforward 2nd Gain', -1, read, 2)

    ##    servos.transmit_packet('Torque Enable', 0, write, 4)

    ##    servos.transmit_packet('Goal Position', 2048, write, 2)
    ##    time.sleep(10)
    ##    servos.transmit_packet('Goal Position', 2048, write, 3)
    ##    servos.transmit_packet('Goal Position', 3072, write, 4)
    ##    time.sleep(10)
    ##    servos.transmit_packet('Goal Position', 2048, write, 2)
    ##    time.sleep(10)
    ##    servos.transmit_packet('Goal Position', 2120, write, 4)
    ##    time.sleep(10)
    ##    servos.transmit_packet('Goal Position', 2048, write, 1)
    ##    time.sleep(15)
    servos.transmit_packet('Goal Position', 2048, sync_write, sync_id)

    ##    time.sleep(5)
    ##
    ####    servos.animate()

    ##
    ##    servos.transmit_packet('Torque Enable', 0, write, 1)
    ##    servos.transmit_packet('Torque Enable', 0, write, 2)
    ##    servos.transmit_packet('Torque Enable', 0, write, 3)
    ##    servos.transmit_packet('Torque Enable', 0, write, 4)
    ####
    ##    while 1:
    ##        print("ELBOW SERVO")
    ##        servos.transmit_packet('Present Position', -1, read, 1)
    ##        print("SHOULDER SERVO 1")
    ##        servos.transmit_packet('Present Position', -1, read, 2)
    ##        print("SHOULDER SERVO 2")
    ##        servos.transmit_packet('Present Position', -1, read, 3)
    ##        print("WAIST SERVO")
    ##        servos.transmit_packet('Present Position', -1, read, 4)
    ##        time.sleep(10)
    ##    time.sleep(5)
    ##    servos.transmit_packet('Goal Position', 1070, write, 2)
    ##    time.sleep(5)
    ##    servos.transmit_packet('Goal Position', 2048, write, 2)
    ##        time.sleep(8)
    ##        servos.transmit_packet('Goal Position', 1536, write, 2)
    ##        time.sleep(8)
    ##        servos.transmit_packet('Goal Position', 2048, write, 2)
    ##        time.sleep(8)
    ##        servos.transmit_packet('Goal Position', 1170, write, 2)
    ##        time.sleep(8)
    ##        servos.transmit_packet('Goal Position', 2048, write, 2)
    ##    servos.transmit_packet('Goal Position',  2048, write, 3)
    ##    time.sleep(8)
    ##    servos.transmit_packet('Moving Status', -1, read, 3)

    ##    servos.transmit_packet('Moving Status', -1, read, 1)
    ##    servos.transmit_packet('Goal Position',  2048, write, 2)
    ##    time.sleep(8)
    ##    servos.transmit_packet('Moving Status', -1, read, 2)
    ##    servos.transmit_packet('Present Position', -1, read, 2)

    ##    servos.transmit_packet('Goal Position',  1229, write, 1)
    ##    time.sleep(5)
    ##    servos.transmit_packet('Present Position', -1, read, 1)
    ##    servos.transmit_packet('Goal Position', 1150, write, 2)
    ##    time.sleep(8)
    ##    servos.transmit_packet('Present Position', -1, read, 2)
    ##    servos.transmit_packet('Goal Position',  3120, write, 3)
    ##    time.sleep(5)
    ##    servos.transmit_packet('Present Position', -1, read, 3)
    ##    servos.transmit_packet('Goal Position', 1536, write, 2)
    ##    time.sleep(8)
    ##    servos.transmit_packet('Present Position', -1, read, 2)
    ##    servos.transmit_packet('Goal Position',  741, write, 1)
    ##    time.sleep(5)
    ##    servos.transmit_packet('Present Position', -1, read, 1)
    ##    servos.transmit_packet('Goal Position', 1170, write, 2)
    ##    time.sleep(8)
    ##    servos.transmit_packet('Present Position', -1, read, 2)
    ##    servos.transmit_packet('Goal Position',  2048, write, 3)
    ##    time.sleep(8)
    ##    servos.transmit_packet('Present Position', -1, read, 3)
    ##    servos.transmit_packet('Goal Position',  1024, write, 1)
    ##    time.sleep(5)
    ##    servos.transmit_packet('Present Position', -1, read, 1)
    ##    servos.transmit_packet('Goal Position',  2048, write, 2)
    ##    time.sleep(8)
    ##    servos.transmit_packet('Present Position', -1, read, 2)
    ##    servos.animate()

    # Position 1
    # Servo_1: 1229
    # Servo_2: 1140
    # Servo_3: 3120
    # Position 2
    # Servo_1: 741
    # Servo_2: 1140
    # Servo_3: 3120
    ##    servos.transmit_packet('LED', 1, write, servo_id)
    ##    servos.transmit_packet('Profile Velocity', 60, write, servo_id) # 60 x 0.229 = 13.74 rpm
    ##    servos.transmit_packet('Profile Acceleration', 10, write, servo_id)
    ##    servos.transmit_packet('Present Load', -1, read, servo_id)
    ####    servos.transmit_packet('Present Input Voltage', -1, read, servo_id)
    ##    servos.transmit_packet('Position P Gain', 600, write, servo_id)
    ##    servos.transmit_packet('Position D Gain', 2000, write, servo_id)
    ##    servos.transmit_packet('Position I Gain', 75, write, servo_id)
    ##    servos.transmit_packet('Torque Enable', 1, write, servo_id)
    ##    servos.transmit_packet('Goal Position',  2048, write, servo_id)
    ##    servos.transmit_packet('Present Position', -1, read, servo_id)
    ##    servos.transmit_packet('Present Position', -1, read, servo_id)
    ##    servos.transmit_packet('Present Position', -1, read, servo_id)
    servos.terminate_serial()