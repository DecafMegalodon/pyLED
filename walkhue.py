#Creates a slowly "walking" color change, in rainbow order
import pyLED
import connect
import time
import random

arduino = connect.get_centralized_connection()

slowness = 7

# while True:
for hue in range(slowness):
    print(hue/slowness)
    for led in range(connect.num_LED):
        arduino.set_HSV(led, (hue/slowness), 1, .4, send=True)
        arduino.display()
        #time.sleep(1)