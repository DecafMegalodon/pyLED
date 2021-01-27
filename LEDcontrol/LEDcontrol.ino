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

void setup() {
  Serial.begin(115200);
  if (Serial.available() < 2) {  //Wait until we know how many LEDs are in the strip. 2 bytes.
    
  }
  
  //Init strip data
  //Set all LEDs to off
  //Send 0x00 over serial to indicate completion?
//  FastLED.addLeds<NEOPIXEL, DATA_PIN>(leds, NUM_LEDS);
//  for(int i = 0; i < NUM_LEDS; i++)
//  {
//    leds[i] = 0x000000;
//    FastLED.show();
//  }

}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 3) {
    Serial.readBytesUntil('þ', serialBuffer,4);
    if(serialBuffer[0] != 0xFF)
    {
      //Serial.println("Update LED");
      leds[serialBuffer[0]].r = serialBuffer[1];
      leds[serialBuffer[0]].g = serialBuffer[2];
      leds[serialBuffer[0]].b = serialBuffer[3];
      //Serial.print("\n");
    }
    else
    {
      //Serial.println("Flush to strip");
      FastLED.show();
      //delay(500);
      Serial.print("\n");
    }
  }

}
