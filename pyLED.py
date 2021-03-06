import serial
import colorsys

class LED:
    def __init__(self, red = 0, blue = 0, green = 0):
        self.red, self.blue, self.green  = red, blue, green
        self.hue, self.sat, self.val = colorsys.rgb_to_hsv(red, blue, green)
        self.rgb_dirty = False  #Mark RGB/HSV as "dirty" to signal it needing recalculation from the other value
        self.hsv_dirty = False
        
    def set_HSV(self, hue = None, sat = None, val = None):
        '''Update a pixel's HSV data. If any parameter is not specified, it will remain unchanged'''
        self.hue, self.sat, self.val = (hue or self.hue), (sat or self.sat), (val or self.val)
        self.hsv_dirty = False
        self.rgb_dirty = True
        
    def set_RGB(self, r = None, g = None, b = None):
        '''Update a pixel's RGB data. If any parameter is not specified, it will remain unchanged'''
        self.red, self.blue, self.green = (r or self.red), (g or self.green), (b or self.blue)
        self.hsv_dirty = True
        self.rgb_dirty = True
        
    def read_rgb(self):
        '''Returns an RGB tuple, calculating the values as needed from HSV'''
        if self.rgb_dirty:
            #maintain RGB in 0..255 range  for native use with LEDs even though colorsys uses 0..1 range
            self.red, self.blue, self.green  = [int(c*255) for c in colorsys.hsv_to_rgb(self.hue, self.sat, self.val)]
            rgb_dirty = False
        return self.red, self.blue, self.green

class LedStrip:
    def __init__(self, port_name, led_count, baud=115200):
        self.data_dirty = False  #Do we need to set LEDs on the arduino to display the current colors?
        self.num_led = led_count
        self.LED_data = [LED() for a in range(led_count)]
        self.zones = {"all": {"data":self.LED_data, 
                                        "start":0, 
                                        "length": led_count-1, 
                                        "increment":1}}
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
        '''Send a packed command to the arduino.
        opcode may be up to 4 bits, arg0 12, and arg 1-3 up to 8 bits
        Command serial format is as such:
        4 bits: command, 
        12 bits, 8 bits, 8 bits, 8 bits: Nominally representing LED number along with  red, blue and green channels
        
        Current opcodes include:
        0: set a single LED's (arg0) RGB to arg1 .. arg3
        1: "Draw" the previously sent RGB values
        2: Set all LEDs to a single RGB value efficiently. RGB stored as arg1 .. arg3
        3: Set LEDs to a max saturation/value rainbow. Command arguments are custom and non-standard for this command.
            arg0 indicates the start of the rainbow
            arg1 indicates the number of LEDs inclued in the rainbow (limited to 255 in a single command invocation)
            arg2 is the starting hue. It is represented in 0...255 versus 0...1 like much of the rest of the code here.
            arg3 is the step between hues per LED
        4: Initiates a full-strip update of all pixels. It should be followed by the red, green, and blue values for all pixels of the strip with no other data
        15: Is a special command. It's used to query data from the arduino. Currently only returns the number of LEDs known to be on the LED strip (used in initialization mostly)
        '''
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

    def set_HSV(self, lednum, h, s, v, send=False):
        '''set HSV for a specific LED at lednum. 
            Optional `send` parameter to immediate update (but not draw) the arduino data for the LED
            See set_RBG for more information on when to use this option'''
        led = self.LED_data[lednum]
        led.set_HSV(h,s,v)
        if not send: #Update the LED but don't send it (Yet)
            self.data_dirty = True
        else: #Immediately send the update to the arduino
            self.send_command(0, lednum, *(led.read_rgb()))
        
    def set_RGB(self, lednum, r, g, b, send=False):
        '''set RGB for a specific LED at lednum. 
            Optional `send` parameter to immediate update (but not draw) the arduino data for the LED
                Recommended when you intend to only update a very small number of LEDs per draw
                When updating a single LED on a strip of 110, using True resulted in almost 400% more draws/second
                When using True for a whole-strip update, expect half as many updates/second vs False'''
        led = self.LED_data[lednum]
        led.set_RGB(r,g,b)
        if not send: #Update the LED but don't send it (Yet)
            self.data_dirty = True
        else: #Immediately send the update to the arduino
            self.send_command(0, lednum, r, g, b)
        
    def set_HSV_all(self, h, s, v, zone="all"):
        '''Set HSV for ALL pixels in a zone'''
        work_zone = self.zones[zone]
        work_zone["data"][0].set_HSV(h, s, v)
        r, g, b = work_zone["data"][0].read_rgb() #Get RGB value by updating the first LED and reading the converted RGB.
        self.set_RGB_all(r, g, b, zone)
        
    def set_RGB_all(self, r, g, b, zone="all"):
        '''Set RGB for ALL pixels in zone'''
        work_zone = self.zones[zone]
        for led in work_zone["data"]:
            led.set_ RGB(r, g, b)
        
        if work_zone["length"] > 255:
            print("Zone lengths over 255 NYI")
        else:
            self.send_command(5, work_zone["start"], 
                                                    0, 
                                                    work_zone["length"], 
                                                    work_zone["increment"])
            self.serial_con.write([r,g,b])
        self.send_command(2, 0, r, g, b)
        
    def define_zone(self, name, start, length, increment=1):
        self.zones[name] = {"data":self.LED_data[start:length:increment], 
                                        "start":start, 
                                        "length": length, 
                                        "increment": increment}