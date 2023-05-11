import socket #pip install socketst
from serial import Serial #pip install serial (pyserial?)
from _thread import *
from threading import Lock

def modbusCrc(msg:str) -> int:
    crc = 0xFFFF
    for n in range(len(msg)):
        crc ^= msg[n]
        for i in range(8):
            if crc & 1:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc

serial = Serial()
serial.port = "/dev/ttyUSB0"
serial.baudrate = 19200
serial.stopbits = 1
serial.parity = "N"
serial.bytesize = 8
serial.timeout = 1
serial.open()

lock = Lock()

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
            rtu_request = tcp_request[6:] + modbusCrc(tcp_request[6:]).to_bytes(2, 'little')
            serial.flushInput()
            serial.write(rtu_request) 
            rtu_response = serial.read(3)

            if len(rtu_response) > 0:
                code = rtu_response[1]
#         
                #https://www.simplymodbus.ca/FC01.htm

                if code == 1 or code == 3:
                    length = rtu_response[2]
                elif code == 6:
                    length = 3

                rtu_response += serial.read(length + 2)
                tcp_response = tcp_request[0:4] + (len(rtu_response)-2).to_bytes(2,'big') + rtu_response[0:-2]
          
                connection.send(tcp_response)

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

start_server("", 1502)
