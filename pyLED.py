import serial
import colorsys

class LED:
    def __init__(self, red = 0, blue = 0, green = 0):
        self.red, self.blue, self.green  = red, blue, green
        self.hue, self.sat, self.val = colorsys.rgb_to_hsv(red, blue, green)
        self.rgb_dirty = False  #Mark RGB/HSV as "Dirty" and needing recalculation from the other value
        self.hsv_dirty = False
        
    def set_HSV(self, hue = None, sat = None, val = None):
        '''Update a pixel's HSV data. If any parameter is not specified, it will remain unchanged'''
        self.hue, self.sat, self.val = (hue or self.hue), (sat or self.sat), (val or self.val)
        self.hsv_dirty = False
        self.rgb_dirty = True
        
    def set_RGB(self, r = None, g = None, b = None):
        self.red, self.blue, self.green = (r or self.r), (g or self.g), (b or self.b)
        self.hsv_dirty = True
        self.rgb_dirty = True
        
    def read_rgb(self):
        if self.rgb_dirty:
            #maintain RGB in 0..255 range  for native use with LEDs even though colorsys uses 0..1 range
            self.red, self.blue, self.green  = [int(c*255) for c in colorsys.hsv_to_rgb(self.hue, self.sat, self.val)]
            rgb_dirty = False
        return self.red, self.blue, self.green

class LedStrip:
    def __init__(self, port_name, led_count, baud=115200):
        data_dirty = False  #Do we need to set LEDs on the arduino to display the current colors?
        self.num_led = led_count
        self.LED_data = [LED() for a in range(led_count)]
        try:
            self.serial_con = serial.Serial(port=port_name, baudrate=baud, timeout=1)
            if self.serial_con.is_open:
                self.serial_con.write([0xF0,00,00,00,00])
                result = int(self.serial_con.readline())
                if result == 0:  #Not yet initialized (or something went wrong previously)
                    print("Initializing..")
                    byte1 = led_count % 256
                    byte0 = (led_count - byte1) >> 8
                    self.serial_con.write([byte0, byte1])
                    result = int(self.serial_con.readline())
                if result == led_count:
                    print("Serial conection established and verified")
                    return
                else:
                    print("Was not able to verify returned value: ", result)
                    print("Do you need to reset the arduino or change the baud rate?")
                    exit(1)
            else:
                print("Didn't manage to conect. Retrying...")  #Todo: Make it actually retry
        except  OSError as e:  #This mostly triggers from being supplied an incorrect serial port
            print(e)
            exit(-1)
            
    def send_command(self, opcode, arg0, arg1, arg2, arg3):
        bytes_0_and_1 = opcode << 12
        bytes_0_and_1 += arg0
        byte_1 = bytes_0_and_1 % 256
        byte_0 = (bytes_0_and_1 - byte_1) >> 8
        self.serial_con.write([byte_0, byte_1, arg1, arg2, arg3])
            
    def display(self):
        '''Sends data to the arduino as needed and instructs it to display the colors on the LED strip'''
        if self.data_dirty:
            self.send_command(4, 0, 0, 0, 0)  #initiate full-strip update mode
            for led in self.LED_data:
                self.serial_con.write(bytearray(led.read_rgb()))
            self.data_dirty = False
            #  The LEDs will be automatically drawn after all data is sent
        else:
            self.send_command(1, 0, 0, 0, 0)
        self.serial_con.readline() #Wait for confirmation from the arduino that the op is complete

    def set_HSV(self, lednum, h, s, v):
        led = self.LED_data[lednum]
        led.set_HSV(h,s,v)
        self.data_dirty = True
        
    def set_RGB(self, lednum, r, g, b):
        led = self.LED_data[lednum]
        led.set_RGB(r,g,b)
        self.data_dirty = True
        
    def set_HSV_all(self, h, s, v):
        for led in self.LED_data:
            led.set_HSV(h, s, v)
        self.LED_data[0].read_rgb()
        #Force HSV->RGB update on the first LED and read the converted RGB.
        self.send_command(2, 0, *(self.LED_data[0].read_rgb()) )
        #Although some LEDs might be marked dirty for recomputation, the data on the arduino matches that new color data
        self.data_dirty = False
        
    def set_RGB_all(self, r, g, b):
        for led in self.LED_data:
            led.red, led.green, led.blue  = r, g, b
            led.rgb_dirty = False
            led.hsv_dirty = True
        self.send_command(2, 0, r, g, b)
        self.data_dirty = False