import random
import time
import pyLED

arduino = pyLED.LedStrip("/dev/ttyACM0", 110)
while True:
    arduino.set_HSV_all(random.random(), 1, .5)
    arduino.display()
    time.sleep(1)