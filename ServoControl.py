import serial
import crcmod
import struct
import ASUS.GPIO as GPIO
import time
from Registers import Registers
import struct


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
        print('Packet: ' + ":".join("{:02x}".format(c) for c in packet))

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
                print("Desired value: ", desired_value)
                parameter_3 = int(desired_value[6:8], 16)  # First Byte
                parameter_4 = int(desired_value[4:6], 16)  # Second Byte
                parameter_5 = int(desired_value[2:4], 16)  # Third Byte
                parameter_6 = int(desired_value[:2], 16)  # Forth Byte
                parameters = [parameter_1, parameter_2, parameter_3, parameter_4, parameter_5, parameter_6]
        else:
            if address == 84:
                desired_value = hex(position)[2:].zfill(byte_count * 2)
                print(desired_value)
                parameter_3 = int(desired_value[2:4], 16)  # First Byte
                print("Parameter3: ", parameter_3)
                parameter_4 = int(desired_value[:2], 16)  # Second Byte
                print("Parameter4: ", parameter_4)
                parameters = [parameter_1, parameter_2, parameter_3, parameter_4]
            else:
                parameters = [parameter_1, parameter_2, parameter_3]
        return parameters

    def transmit_packet(self, command, position, operation, servo_id):
        parameters = self.calculate_parameters(command, position)
        print("PARAM", parameters)
        packet = self.generate_packet(servo_id, operation, parameters)
        try:
            GPIO.output(self.direction_pin, GPIO.HIGH)
            time.sleep(0.000001)
            self.serial_connection.flushInput()
            self.serial_connection.write(packet)
            print("Sending Packet")
            time.sleep(0.0002)  # Time taken for bits to be sent to servo @ 1Mbps
            time.sleep(0.000001)
            GPIO.output(self.direction_pin, GPIO.LOW)
            time.sleep(0.1)  # Return time delay
            print("Receiving Packet")
            self.read_packet()
            self.serial_connection.flushInput()
        except:
            print("Error occurred")

    def read_packet(self):
        self.serial_connection.flushOutput()
        header = self.serial_connection.read(3)
        print("Header: ", header)
        body = self.serial_connection.read(5)
        parameter_count = body[2] - 4
        print("Parameter count: ", parameter_count)
        error = self.serial_connection.read(1)
        print("Error: ", error)
        if parameter_count > 0:
            parameters = self.serial_connection.read(parameter_count)
            print(parameters)
            position = struct.unpack('<I', parameters)[0]
            print(position)
        crc_1 = self.serial_connection.read(1)
        crc_2 = self.serial_connection.read(1)
        print("CRCs: ", crc_1, crc_2)

    def terminate_serial(self):
        self.serial_connection.close()
        GPIO.cleanup()


if __name__ == '__main__':
    ping = 0x01
    read = 0x02
    write = 0x03
    reboot = 0x08
    clear = 0x10
    # Servo_1_Limits: 1536(left), 1024 (mid), 512(right)
    # Servo_2_Limits: 3072(left), 2048 (mid), 1536(right)
    ids = [1, 2, 3]
    servos = ServoControl()
    servos.pin_setup()
    servos.serial_setup()
    servo_id = 1
    servos.transmit_packet('Present Position', -1, read, servo_id)

    servos.transmit_packet('LED', 0, write, servo_id)
    ##    servos.transmit_packet('Present Input Voltage', -1, read, servo_id)
    ##    servos.transmit_packet('Present Position', -1, read, servo_id)
    ##    servos.transmit_packet('Position P Gain', 200, write, servo_id)
    ##    servos.transmit_packet('Position D Gain', 2000, write, servo_id)
    ##    servos.transmit_packet('Position I Gain', 75, write, servo_id)
    servos.transmit_packet('Torque Enable', 1, write, servo_id)
    servos.transmit_packet('Goal Position', 1024, write, servo_id)
    ##    time.sleep(4)
    ##    servos.transmit_packet('Present Position', -1, read, servo_id)
    servos.terminate_serial()