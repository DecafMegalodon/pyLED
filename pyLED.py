import serial
import time
import colorsys
import itertools  #LED signal sending

class LED:
    def __init__(self, red = 0, blue = 0, green = 0):
        self.red, self.blue, self.green  = red, blue, green
        self.hue, self.saturation, self.val = colorsys.rgb_to_hsv(red, blue, green)
        rgb_dirty = False  #Mark RGB/HSV as "Dirty" and needing recalculation from the other value
        hsv_dirty = False
        
    def read_rgb(self):
        if self.rgb_dirty:
            #maintain RGB in 0..255 range  for native use with LEDs even though colorsys uses 0..1 range
            self.red, self.blue, self.green  = [int(c*255) for c in colorsys.hsv_to_rgb(self.hue, self.sat, self.val)]
            rgb_dirty = False
        return self.red, self.blue, self.green

class LedStrip:
    def __init__(self, port_name, led_count, baud=115200):
        self.num_led = led_count
        self.LED_data = [LED(255, 0, 0)] * led_count
        try:
            self.serial_con = serial.Serial(port=port_name, baudrate=baud, timeout=1)
            if self.serial_con.is_open:
                byte2 = led_count % 256
                byte1 = (led_count - byte2) >> 8
                barry = bytearray()
                barry.append(byte1)
                barry.append(byte2)
                self.serial_con.write(barry)
                result = self.serial_con.readline()
                if int(result) == led_count:
                    print("Serial conection established and verified")
                    return
                else:
                    print("Was not able to verify returned value.")
                    print("Do you need to reset the arduino or change the baud rate?")
                    exit(1)
            else:
                print("Didn't manage to conect. Retrying...")  #Todo: Make it actually retry
        except  OSError as e:
            print(e)
            
    def send_command(self, opcode, arg0, arg1, arg2, arg3):
        assert opcode < (2**4)  #Also don't do negative values. Temporary asserts for testing
        assert arg0 < (2**12)
        assert arg1 < (2**8)
        assert arg2 < (2**8)
        assert arg3 < (2**8)
        bytes_0_and_1 = opcode << 12  #Todo: Clean this dumpster fire up!!
        bytes_0_and_1 += arg0
        byte_1 = bytes_0_and_1 % 256
        byte_0 = (bytes_0_and_1 - byte_1) >> 8
        barry = bytearray()
        barry.append(byte_0)
        barry.append(byte_1)
        barry.append(arg1)
        barry.append(arg2)
        barry.append(arg3)
        self.serial_con.write(barry)
            
    def draw(self):
        self.send_command(1, 0, 0, 0, 0)
        self.serial_con.readline() #Wait for confirmation from the arduino that the op is complete
        
    def update(self):
        '''Updates the arduino's LED color data'''
        #Todo: Implement heuristics to decide between per-pixel updates for a small number and a lower-overhead full strip update
        self.send_command(4, 0, 0, 0, 0)  #initiate full-strip update mode
        for led in self.LED_data:
            self.serial_con.write(bytearray(led.read_rgb()))
        self.serial_con.readline() #Wait for confirmation from the arduino that the op is complete

    def set_HSV_all(self, h, s, v):
        for led in self.LED_data:
            led.hue, led.sat, led.val = h, s, v
            led.rgb_dirty = True
        self.send_command(2,0,*(self.LED_data[0].read_rgb() ) )  #Force RGB update on the first LED. Ugly kludge or DRY? You decide.
        
        
    def set_RGB_all(self, r, g, b):
        for led in range(self.num_led):
            self.LED_data[led].red  = r
            self.LED_data[led].green  = g
            self.LED_data[led].blue  = b
        self.send_command(2, 0, r, g, b)
    
arduino = LedStrip("/dev/ttyACM0", 110)
slowness = 80
while True:
    for hue1 in range(0, 7):
        hue = hue1/7
        print(hue)
        for val1 in range(0,slowness,1):
            val = val1/slowness
            arduino.set_HSV_all(hue, 1, val)
            #arduino.update()
            arduino.draw()
        for val1 in range(slowness,0,-2):
            val = val1/slowness
            arduino.set_HSV_all(hue, 1, min(val,1))
            #arduino.update()
            arduino.draw()