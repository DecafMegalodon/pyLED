import serial
import time
num_led = 15

#returns a serial connection object that can be read from an written to.
#Initialized the number of LEDs and verifies that the arduino is good to go
#  Blocks until a connection is established
def init_connection(port_name, baud, led_count):
    try:
        conn = serial.Serial(port=port_name, baudrate=baud, timeout=1)
        if conn.is_open:
            byte2 = led_count % 256
            byte1 = (led_count - byte2) >> 8
            barry = bytearray()
            barry.append(byte1)
            barry.append(byte2)
            conn.write(barry)
            if int(conn.readline()) == led_count:
                print("Connection established and verified")
                return conn
            else:
                print("Was not able to verify returned value.")
                print("Do you need to reset the arduino or change the baud rate?")
                exit(1)
        else:
            print("Didn't manage to connect. Retrying...")  #Todo: Make it actually retry
    except:
        print("There was an error establishing a serial connection.")
        print("Likely an invalid or unconnected serial port.")
        exit(1)

#Sends a command to the arduino.
#Bit lengths:
#Opcode:4, arg0:12, arg1-3: 8
def send_command(conn, opcode, arg0, arg1, arg2, arg3):
    assert opcode < (2**4)  #Also don't do negative values. Temporary asserts for testing
    assert arg0 < (2**12)
    assert arg1 < (2**8)
    assert arg2 < (2**8)
    assert arg3 < (2**8)
    bytes_0_and_1 = opcode << 12
    bytes_0_and_1 += arg0
    byte_1 = bytes_0_and_1 % 256
    byte_0 = (bytes_0_and_1 - byte_1) >> 8
    barry = bytearray()
    barry.append(byte_0)
    barry.append(byte_1)
    barry.append(arg1)
    barry.append(arg2)
    barry.append(arg3)
    conn.write(barry)
    if opcode == 1:
        conn.readline()
    
    

arduino = init_connection("/dev/ttyACM0", 115200, 110)
while True:
    for hue in range(0,255,1):
        send_command(arduino, 3, 0, 110, hue, 1)
        send_command(arduino, 1, 0, 0, 0, 0)
