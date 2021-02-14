import pyLED

num_LED = 110
port_name = "/dev/ttyACM0"

def get_centralized_connection():
  return pyLED.LedStrip(port_name, num_LED)