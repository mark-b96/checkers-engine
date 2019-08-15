import serial
import crcmod
import struct
import ASUS.GPIO as GPIO
import time
from Registers import Registers


class ServoControl(object):
    def __init__(self):
        self.baud_rate = 57600
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

    def serial_setup(self):
        try:
            self.serial_connection = serial.Serial(self.serial_port, self.baud_rate, self.timeout)
        except:
            print("Error connecting to serial port")

    def generate_packet(self, servo_id, instruction, packet_parameters):
        parameter_count = len(packet_parameters)
        packet_length = parameter_count + 3
        packet = [0xff, 0xff, 0xfd, 0x00, servo_id, packet_length, 0, instruction]
        for parameter in packet_parameters:
            packet.append(parameter)
        print(packet)
        packet = bytearray(packet)
        print(packet)
        self.calculate_crc(packet)
        return packet

    def calculate_crc(self, packet):
        crc_fun = crcmod.mkCrcFun(0x18005, initCrc=0, rev=False)  # Calculate CRC1 and CRC2
        crc = crc_fun(bytes(packet))  # Convert binary value to byte_count
        packet.extend(struct.pack('<H', crc))
        print('Packet: ' + ":".join("{:02x}".format(c) for c in packet))

    @staticmethod
    def calculate_parameters(command):
        r = Registers()
        address = r.get_address(command)
        byte_count = r.get_bytes(command)
        parameter_1 = address  # Low-order byte from the starting address
        parameter_2 = 0x00  # High-order byte from the starting address
        parameter_3 = 0x01  # Turn on

        if byte_count > 2:
            desired_value = hex(512)[2:].zfill(byte_count*2)
            parameter_3 = int(desired_value[:2])  # First Byte
            parameter_4 = int(desired_value[4:6])  # Second Byte
            parameter_5 = int(desired_value[2:4])  # Third Byte
            parameter_6 = int(desired_value[:2])  # Forth Byte
            parameters = [parameter_1, parameter_2, parameter_3, parameter_4, parameter_5, parameter_6]
        else:
            if address == 84:
                parameter_3 = 80
            parameters = [parameter_1, parameter_2, parameter_3]
        return parameters

    def transmit_packet(self, command):
        parameters = self.calculate_parameters(command)
        print(parameters)
        servo_id = 0x01
        packet = self.generate_packet(servo_id, self.write, parameters)
        try:
            GPIO.output(self.direction_pin, GPIO.HIGH)
            self.serial_connection.flushInput()
            self.serial_connection.write(packet)
            print("Sending Packet")
            time.sleep(0.1)
            GPIO.output(self.direction_pin, GPIO.LOW)
            print(self.serial_connection.read(16))
        except:
            print("Error occurred")

    def terminate_serial(self):
        self.serial_connection.close()
        GPIO.cleanup()


if __name__ == '__main__':
    servos = ServoControl()
    servos.transmit_packet('LED')
    servos.transmit_packet('Torque Enable')
    servos.transmit_packet('Goal Position')
    servos.transmit_packet('Position P Gain')
    servos.transmit_packet('Goal Position')

