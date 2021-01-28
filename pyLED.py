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
            byte1 = led_count % 256
            byte2 = (led_count - byte1) >> 8
            barry = bytearray()
            barry.append(byte1)
            barry.append(byte2)
            conn.write(barry)
            return conn
        else:
            print("Didn't manage to connect. Retrying...")
    except:
        print("There was an error establishing a serial connection.")
        print("Likely an invalid or unconnected serial port.")
        exit(1)

arduino = init_connection("/dev/ttyACM0", 115200, 15)
