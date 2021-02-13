#Creates a slowly cycling rainbow across the entire LED strip
import pyLED
import connect

arduino = connect.get_centralized_connection()

slowness = 1080

while True:
    for hue in range(slowness):
        arduino.set_HSV_all((hue/slowness), 1, .4)
        arduino.display()