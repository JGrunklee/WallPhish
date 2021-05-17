# Quick neopixel test / sanity check for later
# Adapted from Adafruit's Raspberry Pi Neopixel Guide
# https://learn.adafruit.com/neopixels-on-raspberry-pi/python-usage


import time
import board
import neopixel

pixel_pin = board.D18

num_pixels = 3

ORDER = neopixel.RGB

pixels = neopixel.Neopixel(
    pixel_pin, num_pixels, brightness=0.2, auto_write=False,
    pixel_order=ORDER
    )
    
if __name__ == '__main__':
    pixels.fill ... tbd