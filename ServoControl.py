import serial
import crcmod
import struct
import ASUS.GPIO as GPIO
import time

BAUDRATE = 57600
channel = 12
try:
    ser = serial.Serial('/dev/ttyS1', BAUDRATE, timeout=0.05)
    print(ser.name)
except:
    print("ERROR")
GPIO.setmode(GPIO.BOARD)
GPIO.setup(channel, GPIO.OUT)

packet_id = 0x04  # Servo ID
param_count = 3  # Number of parameters
packet_length = param_count + 3
instruction = 0x03  # Write
Param_1 = 0x41  # Low-order byte from the starting address
Param_2 = 0x00  # High-order byte from the starting address
Param_3 = 0x01  # First Byte
# Param_4 = 0x02
# Param_5 = 0x00
# Param_6 = 0x00
packet = bytearray([0xff, 0xff, 0xfd, 0x00, packet_id, packet_length, 0, instruction, Param_1, Param_2, Param_3])

crc_fun = crcmod.mkCrcFun(0x18005, initCrc=0, rev=False)  # Calculate CRC1 and CRC2
crc = crc_fun(bytes(packet))  # Convert binary value to bytes

packet.extend(struct.pack('<H', crc))
print(packet)
print('Packet: ' + ":".join("{:02x}".format(c) for c in packet))
print('Packet: ' + ":".join("{:08b}".format(c) for c in packet))
print('Packet: ' + ":".join("{:.3g}".format(c) for c in packet))

try:
    GPIO.output(channel, GPIO.HIGH)
    ser.flushInput()
    ser.write(packet)
    print("Sending Packet")
    time.sleep(0.1)
    GPIO.output(channel, GPIO.LOW)
    print(ser.read(16))
##    header = ser.read(3)
##    print("Received header: "+ ":".join("{:02x}".format(ord(c)) for c in header))
##body = ser.read(4)
##print("Received body: "+ ":".join("{:02x}".format(ord(c)) for c in body))

except:
    print("Error occurred")
ser.close()
GPIO.cleanup()