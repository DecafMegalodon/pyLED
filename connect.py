import pyLED

num_LED = 110

def get_centralized_connection():
  return pyLED.LedStrip("/dev/ttyACM1", num_LED)