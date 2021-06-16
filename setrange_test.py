#Creates a slowly "walking" color change, in rainbow order
import pyLED
import connect
import time
import random

arduino = connect.get_centralized_connection()
arduino.send_command(2, 0, random.randint(0,16), random.randint(0,16), random.randint(0,16))
arduino.display()
time.sleep(2)
print("yeehaw!")
for start in range(0, 10):
    for skip in range(1, 5):
        print(start, skip)
        #def send_command(self, opcode, arg0, arg1, arg2, arg3):
        arduino.send_command(2, 0, 0, 0, 0)
        arduino.send_command(5, start, 0, 20, skip)
        arduino.serial_con.write([255,0,0])
        arduino.display()
        time.sleep(.1)