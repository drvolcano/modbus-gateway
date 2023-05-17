
import socket #pip install socketst
from serial import Serial #pip install serial (pyserial?)
from _thread import *
from threading import Lock
import time
from Crypto.Cipher import AES #pip install pycrypto

#684b4b6808217233050305a5114004920000000c06822202008c1006222102008c2006782202000c13681735000c2b021000000b3b1800000a5a00070a5e20020a6280040b26041601046d0e17f125ab16
#ID: 5030533 MAN:DME MED:HEAT_OUTLET GEN:64
#Identification
     #Product name DME_64 
     #Serial number DME4005030533 
     #Medium Heat outlet 
     #Generation 64 
#Parameter
     #Device time 17.05.2023 23:14 
     #Device time deviation -1 hours, -36 minutes 
#Values
     #17.05.2023 21:37 Heating energy 22282000 Wh
     #17.05.2023 21:37 Energy 22122000 Wh Tariff 1
     #17.05.2023 21:37 Energy 22278000 Wh Tariff 2
     #17.05.2023 21:37 Volume 351,768 m³
     #17.05.2023 21:37 Power 1002 W
     #17.05.2023 21:37 Volume flow 0,018 m³/h
     #17.05.2023 21:37 Flow temperature 70 °C
     #17.05.2023 21:37 Return temperature 22 °C
     #17.05.2023 21:37 Temperature diff 48 °K
     #17.05.2023 21:37 Operating time 1160400 hour

#ID: 5030533 MAN:DME MED:HEAT_OUTLET GEN:64 ACC:146 STA:0 SIG:0

#RESPONSE 81 bytes. 
 #68 4B 4B 68 08 21 72 33 05 03 05 A5 11 40 04 92 00 00 00 
 # 0C   06 82 22 02 00 
 # 8C10 06 22 21 02 00 
 # 8C20 06 78 22 02 00 
 # 0C 13 68 17 35 00 
 # 0C 2B 02 10 00 00 
 # 0B 3B 18 00 00 
 # 0A 5A 00 07 
 # 0A 5E 20 02 
 # 0A 62 80 04 
 # 0B 26 04 16 01 
 # 04 6D 0E 17 F1 25 AB 16                                              
#LongFrame C:RSP_UD_08h ADDR:33 CI:MBusWithFullHeader IsVariableDataStructure:True
#HEADER
      #ID: 5030533 MAN:DME MED:HEAT_OUTLET GEN:64 ACC:146 STA:0 SIG:0
#RECORDS
      #DIF:0Ch (Bcd8) VIF:06h Data:82220200h Energy 22282000 Wh
      #DIF:8Ch (Bcd8) DIFE:10h VIF:06h Data:22210200h Energy 22122000 Wh Tariff:1
      #DIF:8Ch (Bcd8) DIFE:20h VIF:06h Data:78220200h Energy 22278000 Wh Tariff:2
      #DIF:0Ch (Bcd8) VIF:13h Data:68173500h Volume 351.768 m³
      #DIF:0Ch (Bcd8) VIF:2Bh Data:02100000h Power 1002 W
      #DIF:0Bh (Bcd6) VIF:3Bh Data:180000h Volume flow 0.018 m³/h
      #DIF:0Ah (Bcd4) VIF:5Ah Data:0007h Flow temperature 70 °C
      #DIF:0Ah (Bcd4) VIF:5Eh Data:2002h Return temperature 22 °C
      #DIF:0Ah (Bcd4) VIF:62h Data:8004h Temperature diff 48 °K
      #DIF:0Bh (Bcd6) VIF:26h Data:041601h Operating time 1160400 hour
      #DIF:04h (Int32) VIF:6Dh Data:0E17F125h  17.05.2023 23:14
#MDH: 00h




registers = bytearray()

import serial.tools.list_ports
ports = serial.tools.list_ports.comports()
serial = Serial()

for port, desc, hwid in sorted(ports):
    if 'CP2102 ' in desc:
        serial.port = port

serial.baudrate = 300
serial.stopbits = 1
serial.parity = "E"
serial.bytesize = 8
serial.timeout = 3
serial.open()

lock = Lock()


def analyze(bytes):
    result = 0

    for byte in bytes[::-1]:
        result = result * 100
        result = result + (byte & 0x0F) + (byte & 0xF0) // 16 * 10

    #print(result) 


    if len(bytes) > 2:  
        return result.to_bytes(4, 'big')
    else:
        return result.to_bytes(2, 'big')


def amisreader():


    while True:
        #print("ping")
        serial.write(b'b\x10\x7B\xFE\x79\x16')
        time.sleep(0.1)

        part1 = serial.read(4)

        if part1 and part1[0] == part1[3] and part1[1]== part1[2]:
            length = part1[1]
            part2 = serial.read(length )
            part3 = serial.read(2)
            #print(part1+ part2+ part3)
            äprint( ''.join('{:02x}'.format(x) for x in (part1+part2+part3)))

            temp = bytearray()

            temp += analyze( part2[17:17+4])
            temp += analyze( part2[24:24+4])
            temp += analyze( part2[31:31+4])
            temp += analyze( part2[37:37+4])
            temp += analyze( part2[43:43+4])
            temp += analyze( part2[49:49+3])
            temp += analyze( part2[54:54+2])
            temp += analyze( part2[58:58+2])
            temp += analyze( part2[62:62+2])
            temp += analyze( part2[66:66+3])

            global registers
            registers = temp

        
        
def client_handler(connection):
    while True:

        try:
            tcp_request = connection.recv(1024 )
        except BlockingIOError:
            return   # socket is open and reading from it would block
        except ConnectionResetError:
            return   # socket was closed for some other reason
        except Exception as e:
            return

       #print("request(TCP): " + str(tcp_request))

        if not tcp_request:
            return

        if len(tcp_request) >6:
            lock.acquire()
            length= int.from_bytes( tcp_request[4:6],'big')
            rtu_request = tcp_request[6:] 
            address = rtu_request[0]
            code = rtu_request[1]

            #print(str(tcp_request))

            register = int.from_bytes( rtu_request[2:4],'big')
            length = int.from_bytes( rtu_request[4:6],'big')


            data = registers[register*2: (register+length)*2]

            rtu_response = rtu_request[0:2] +  (len(data)).to_bytes(1,'big') + data
        
    
         
      
            tcp_response = tcp_request[0:4] + (len(rtu_response)).to_bytes(2,'big') + rtu_response
            connection.send(tcp_response)
            #print(str(tcp_response))
            lock.release()

def accept_connections(ServerSocket):
    Client, address = ServerSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(client_handler, (Client, ))

def start_server(host, port):
    ServerSocket = socket.socket()
    ServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        ServerSocket.bind((host, port))
    except socket.error as e:
        print(str(e))
    print(f'Server is listing on the port {port}...')
    ServerSocket.listen()

    while True:
        accept_connections(ServerSocket)



start_new_thread(amisreader, ())

start_server("", 1504)
