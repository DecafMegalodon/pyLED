import serial
import time
num_led = 15

#returns a serial connection object that can be read from an written to.
#  Blocks until a connection is established
def create_connection(port_name, baud):
    try:
        conn = serial.Serial(port=port_name, baudrate=baud, timeout=1)
        if conn.is_open:
            return conn
        else:
            print("Didn't manage to connect. Retrying...")
    except:
        print("There was an error establishing a serial connection.")
        print("Likely an invalid or unconnected serial port.")
        exit(1)

arduino = create_connection("/dev/ttyACM0", 115200)
time.sleep(1)
test = bytearray()
test.append(0)
test.append(num_led)
arduino.write(test)
time.sleep(.5)
ardreturn = arduino.readline()
print(ardreturn)
if int(ardreturn) == num_led:
    print("Hooray!")
else:
    print("Womp :(")
