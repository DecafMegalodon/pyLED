#Creates a slowly cycling rainbow across the entire LED strip
import pyLED
import connect

arduino = connect.get_centralized_connection()

slowness = 1080

arduino.define_zone("even", 0, 108, 2)
arduino.define_zone("odd", 1, 107, 2)

while True:
    for hue in range(slowness):
        arduino.set_HSV_all((hue/slowness), 1, .3, zone="even")
        arduino.set_HSV_all((hue/slowness)+.5, 1, .3, zone="odd")
        arduino.display()
