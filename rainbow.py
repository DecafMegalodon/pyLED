import pyLED
import connect

arduino = connect.get_centralized_connection()

slowness = 120

while True:
    for hue in range(slowness):
        for led in range(connect.num_LED):
            arduino.set_HSV(led, (hue/slowness) + (led/connect.num_LED), 1, .4)
        arduino.display()