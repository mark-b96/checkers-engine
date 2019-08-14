import serial
import crcmod
import struct

channel = 12
connected = True
ser = serial.Serial("/dev/ttyACM0", 57600, timeout=1)
GPIO.setmode(GPIO.Board)
GPIO.setup(channel, GPIO.OUT)
# while not connected:
#     serin = ser.read()
#     connected = True

packet_id = 0x01  # Servo ID
param_count = 3  # Number of parameters
packet_length = param_count+3
instruction = 0x03  # Write
Param_1 = 0x41  # Low-order byte from the starting address
Param_2 = 0x00  # High-order byte from the starting address
Param_3 = 0x01  # First Byte
# Param_4 = 0x02
# Param_5 = 0x00
# Param_6 = 0x00
packet = bytearray([0xff, 0xff, 0xfd, 0x00, packet_id, packet_length, 0,  instruction, Param_1, Param_2, Param_3])

crc_fun = crcmod.mkCrcFun(0x18005, initCrc=0, rev=False)  # Calculate CRC1 and CRC2
crc = crc_fun(bytes(packet))  # Convert binary value to bytes

packet.extend(struct.pack('<H', crc))
print(packet)
print('Packet: ' + ":".join("{:02x}".format(c) for c in packet))
print('Packet: ' + ":".join("{:02b}".format(c) for c in packet))
print('Packet: ' + ":".join("{:.3g}".format(c) for c in packet))
cmd = packet
GPIO.output(channel, GPIO.HIGH)
ser.write(cmd)
time.sleep(0.1)
GPIO.output(channel, GPIO.LOW)
time.sleep(1)


#
# while 1:
#     reading = str(ser.readline())
#     ser.flushInput()r
#     if reading:
#         print("Printing reading")
#         print(reading)

    # ser.close()
