# pyLED
pyLED is a high level python library for controlling LED strips and an associated arduino sketch. Its intention is to provide a simple and intuitive way to control LED strip lights in ways that are useful for creating decorative displays.

To get started with pyLED, you'll need an arduino (I use an arduino UNO) and another device with a USB port and the capability to run Python (I use my desktop), as well as a strip of LED lights wired up with any needed power cables hooked up. (WS2812B).

It will require pyserial, which can be install with pip3 install pyserial.

Using Arduino Studio, or another solution, upload and compile the sketch in LEDcontrol/LEDcontrol.ino to the arduino

From there, you will be able to configure connect.py with the number of LEDs your strip has (num_LED) and the port with which your Python device will communicate with the Arduino (port_name). You can find the port for your Arduino on the botom right side of Arduino Studio. Keep in mind that pyLED will not work while Arduino Studio's serial monior is up.

Once pyLED has been configured, you can run many of the demos (hue, rainbow, walkhue) directly with python3 and enjoy the light show! Some system configurations may necessiate running the script twice to initialize the Arduino.
