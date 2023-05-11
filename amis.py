import socket #pip install socketst
from serial import Serial #pip install serial (pyserial?)
from _thread import *
from threading import Lock
from Crypto.Cipher import AES #pip install pycrypto

sampledata = [104, 95, 95, 104, 115, 240, 91, 0, 0, 0, 0, 45, 76, 1, 14, 12, 0, 80, 5, 249, 225, 124, 207, 6, 226, 132, 195, 238, 124, 131, 27, 133, 145, 11, 51, 227, 9, 201, 247, 15, 120, 143, 246, 6, 171, 244, 124, 7, 70, 242, 174, 20, 42, 205, 60, 170, 1, 93, 8, 92, 55, 228, 57, 232, 43, 85, 149, 108, 112, 163, 45, 235, 132, 121, 136, 193, 143, 15, 12, 213, 80, 60, 221, 184, 235, 159, 161, 197, 196, 122, 5, 152, 6, 89, 212, 229, 50, 233, 224, 124, 22]
key = "32D13550827108D59C460D6A9DBAD7BE"
keybytes = bytes(bytearray.fromhex(key))

serial = Serial()
serial.port = "/dev/ttyUSB1"
serial.baudrate = 9600
serial.stopbits = 1
serial.parity = "E"
serial.bytesize = 8
serial.timeout = 1
serial.open()

reading = False
buffer = bytes()
length = 0

while True:
    byte = serial.read(1)

    if not reading and byte == b'\x68':
        buffer = []
        length = 0
        reading = True

    if reading:
        buffer.extend(byte)

        if len(buffer) == 4:
            if buffer[0] == 0x68 and buffer[1] == buffer[2] and buffer[3] == 0x68:
                length = buffer[1]
            else:
                reading = False

        if len(buffer) == (4 + length + 2):
            #print(str(bytes(buffer)))
            content = buffer[4:-2]
            reading = False
            c = content[0]
            a = content[1]
            ci = content[2]
            identification =  content[3:7]
            manufacturer = content[7:9]
            version = content[9]
            devType = content[10]
            access = content[11]
            status = content[12]
            configuration = content[13:15]
            encrypted = content[15:]

            iv = []
            iv.extend(manufacturer)
            iv.extend(identification)
            iv.append(version)
            iv.append(devType)

            for x in range(8):
                iv.append(access)

            ivbytes = bytes(iv)

            obj2 = AES.new(keybytes, AES.MODE_CBC, ivbytes)
            decrypted = obj2.decrypt(bytes(encrypted))

            ary = bytearray(decrypted)

            b066D = int.from_bytes(ary[4:4+6],'little')#Datum M-Bus Format
            b0403 = int.from_bytes(ary[12:12+4],'little')#1.8.0 Wirk Bezug Wh
            b04833C = int.from_bytes(ary[19:19+4],'little')#2.8.0 Wirk Einspeis Wh
            b8410FB8273 = int.from_bytes(ary[28:28+4],'little')#3.8.1 Blind + varh
            b8410FB82F33C = int.from_bytes(ary[38:38+4],'little')#4.8.1 Blind - varh
            b042B = int.from_bytes(ary[44:44+4],'little')#Wirkleistung Bezug W
            b04AB3C = int.from_bytes(ary[51:51+4],'little')#Wirkleistung Einspeis W
            b04FB14 = int.from_bytes(ary[58:58+4],'little')#3.7.0 Blindleistung + W
            b04FB943C = int.from_bytes(ary[66:66+4],'little')#4.7.0 Blindleistung - W
            b0483FF04 = int.from_bytes(ary[74:74+4],'little')#1.128.0 Inkassozählwerk Wh

            print('#############################')
            print(str(a))
            print(str(b))
            print(str(c))
            print(str(d))
            print(str(e))
            print(str(f))
            print(str(g))
            print(str(h))
            print(str(i))

    if byte == b'\x16':
        print("response")

        serial.write(b'\xe5')
