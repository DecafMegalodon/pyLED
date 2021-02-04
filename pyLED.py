import serial
import time

class LedStrip:
    def __init__(self, port_name, led_count, baud=115200):
        self.num_led = led_count
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
                print(result)
                if int(result) == led_count:
                    print("Serial conection established and verified")
                    return
                else:
                    print("Was not able to verify returned value.")
                    print("Do you need to reset the arduino or change the baud rate?")
                    exit(1)
            else:
                print("Didn't manage to self.serial_conect. Retrying...")  #Todo: Make it actually retry
        except  OSError as e:
            print(e)
            
    def send_command(self, opcode, arg0, arg1, arg2, arg3):
        assert opcode < (2**4)  #Also don't do negative values. Temporary asserts for testing
        assert arg0 < (2**12)
        assert arg1 < (2**8)
        assert arg2 < (2**8)
        assert arg3 < (2**8)
        bytes_0_and_1 = opcode << 12
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
        if opcode == 1:  #Wait for confirmation from the arduino that the op is complete
            self.serial_con.readline()
    
arduino = LedStrip("/dev/ttyACM0", 110)
while True:
    for value in range(0,255,1):
        #arduino.send_command(3, 0, 110, value, 1)
        arduino.send_command(2, 0, int(value/2), 0, value)
        arduino.send_command(1, 0, 0, 0, 0)
    for value in range(255,0,-1):
        #arduino.send_command(3, 0, 110, value, 1)
        arduino.send_command(2, 0, int(value/2), 0, value)
        arduino.send_command(1, 0, 0, 0, 0)