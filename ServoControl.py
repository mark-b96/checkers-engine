import serial
import crcmod
import struct

# connected = True
# ser = serial.Serial("/dev/ttyACM0", 57600, timeout=1)
#
# while not connected:
#     serin = ser.read()
#     connected = True

packet_id = 0x01
param_count = 6
packet_length = param_count+3
instruction = 0x03
Param_1 = 0x74
Param_2 = 0x00
Param_3 = 0x00
Param_4 = 0x02
Param_5 = 0x00
Param_6 = 0x00
packet = bytearray([0xff, 0xff, 0xfd, 0x00, packet_id, packet_length, 0,  instruction, Param_1, Param_2, Param_3, Param_4, Param_5, Param_6])

crc_fun = crcmod.mkCrcFun(0x18005, initCrc=0, rev=False)
crc = crc_fun(bytes(packet))  # Convert binary value to bytes

packet.extend(struct.pack('<H', crc))
print('Packet: '+ ":".join("{:02x}".format(c) for c in packet))
# cmd = packet
# ser.write(cmd)
#
# while 1:
#     reading = str(ser.readline())
#     ser.flushInput()r
#     if reading:
#         print("Printing reading")
#         print(reading)

    # ser.close()
