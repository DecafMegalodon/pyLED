pyLED will consist of two parts: the high level API (python) and a low-level arduino interpreter, which recieves communications over USB. This allows a wide range of devices to control an LED strip without any presumption of the precise timing capabilities on the API host.

Interpreter:
 Initialization: 2-bytes, containing the number of LEDs on the strip

5-byte opcodes. Command (4 bit)|LED number (12 bit)|Red intentensity (8)|Green (8)|Blue (8)
  Command 0: Set an LED to an RGB
  Command 1: "Draw" the LED string
  Command 2: Set all LEDs to the RGB value and draw the strip
  Commands 3 - 15: Undefined, at the moment
  
The arduino interpreter's job is mostly to isolate the LED strip from the unreliable timing of the API. WS2812 LED strips require microsecond precision - something we cannot promise on a real-time multiprocess operating system such as Raspbery Pi OS or Ubuntu (although in the Pi's case we can perform some hacks with the PCM GPIO pins to increase this reliability). The goal here is reliability across a range of hosts.
While the interpreter's primary use is to ensure accurate communication between the API host and the LEDs, it has some small additional features planned such as being able to automatically turn off lights on host signal loss and thermal monitoring.


Python API capabilities:
Maintain HSV and RGB values for all LEDs, to reduce unneccesary RGB <-> HSV rounding errors when only working with one or the other.
Send only changed LEDs to the arduino when it's time to "draw" colors on the LEDs to reduce overhead
Defining ranges of LEDs, including non-sequential addresses.
Directly setting the color (RGB or HSV) of a single LED
Setting a solid color (RGB or HSV) of a range.
Setting a hue-based gradient over a range
Fading from one color to another, either directly in RGB or HSV
(Possibly) Setting a custom blink for a range that does not need to repeatedly issue manual commands.
(Possibly) Virtual LEDs which do not correspond to a physical LED. To handle holes between joined strips without a "jump" in lights
