#include <bitswap.h>
#include <chipsets.h>
#include <color.h>
#include <colorpalettes.h>
#include <colorutils.h>
#include <controller.h>
#include <cpp_compat.h>
#include <dmx.h>
#include <FastLED.h>
#include <fastled_config.h>
#include <fastled_delay.h>
#include <fastled_progmem.h>
#include <fastpin.h>
#include <fastspi.h>
#include <fastspi_bitbang.h>
#include <fastspi_dma.h>
#include <fastspi_nop.h>
#include <fastspi_ref.h>
#include <fastspi_types.h>
#include <hsv2rgb.h>
#include <led_sysdefs.h>
#include <lib8tion.h>
#include <noise.h>
#include <pixelset.h>
#include <pixeltypes.h>
#include <platforms.h>
#include <power_mgt.h>

#define DATA_PIN 7

byte serial_buffer[5];
int num_LEDs;
CRGB* leds; //The LED strip data
int instruction;
int cur_LED;
long timeout = 0;

void setup() {
  Serial.begin(115200);
  while (Serial.available() < 2) {}  //Wait until we know how many LEDs are in the strip. 2 bytes.
//  num_LEDs = (serial_buffer[0] << 8) + serial_buffer[1];
  Serial.readBytes((char*) serial_buffer, 2);
  num_LEDs = int(serial_buffer[1]);
  leds = new CRGB[num_LEDs];
  FastLED.addLeds<NEOPIXEL, DATA_PIN>(leds, num_LEDs);
  FastLED.clear();  //Set all pixels to black
  FastLED.show();
  Serial.println(num_LEDs);  //Echo the number of LEDs back to validate baud rate.
  // Pass control over the strip to the computer
}

void loop() {
  while (Serial.available() < 5 ) {
    timeout += 1;
    if(timeout == 21474835){
      FastLED.clear();
      FastLED.show();
      timeout = 0; 
    }
  } //Don't do anything until we have a full command ready
  timeout = 0;  //Reset the auto-blank since we got a command
  Serial.readBytes((char*) serial_buffer, 5);
  
  instruction = serial_buffer[0] >> 4;  //Take only the high 4 bits of byte 1
  cur_LED = (serial_buffer[0] << 12 >> 4) + serial_buffer[1];  //Shift out the high 4 bites of buffer[0] since they're the instruction, not LED data
                                                               //We're operating under the assumption of 16 bit math 
  //Todo: Determine if bit shifting or modular arithmetic are faster on this platform
  
  switch(instruction){
    case(0):  //Write an LED 
      memcpy(&leds[cur_LED], serial_buffer+2, 3);  //Todo: this could probably be optimized more.
      break;
    case(1):  //"Draw" sent LEDs
      FastLED.show();
      Serial.println();  //Send an empty line over serial so the host knows when we can accept input again
      break;
    case(2):  //Set all LEDs to the same color
      fill_solid(leds, num_LEDs, CRGB(serial_buffer[2], serial_buffer[3], serial_buffer[4]));
      break;
    //Set a (Max value and max saturation) hue gradient.
    //Custom operands: cur_LED is the starting LED, R is the number of LEDs (limited to 255), G is the initial hue, and B is the hue step between LEDs
    //If more than 255 LEDs are needed, send a second rainbow draw command
    case(3):
      fill_rainbow(leds+cur_LED, serial_buffer[2], serial_buffer[3], serial_buffer[4]);
      break;
    //Full-string update from host. Draws the string once the transmission is complete
    //After the command is sent, comms should be RGB only until all pixels are updated
    case(4):
      
      break;
    }
}
