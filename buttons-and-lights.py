#!/usr/bin/python3

import atexit
import time

import hid
from keys import Key, Keypad
import leds

def key_int_handler(keynum):
    def h(button):
        if button.is_held:
            print("Button {} held".format(keynum))
        elif button.is_pressed:
            print("Button {} pressed".format(keynum))
        else:
            print("Button {} released".format(keynum))
    return h

gadget = hid.HidGadget('/dev/hidg1')
nkro_report = hid.HidBitmapReport(gadget, 1+31, [(0, 248, 1)])#, report_id=1)

led_map = [3, 7, 11, 2, 6, 10, 1, 5, 9, 0, 4, 8]
keymap = [
        Key(17, key_code=0x04, hid_report=nkro_report),
        Key(27, key_code=0x05, hid_report=nkro_report, handler=key_int_handler(1) ),
        Key(23, key_code=0x06, hid_report=nkro_report),
        Key(22, key_code=0x07, hid_report=nkro_report),
        Key(24, key_code=0x08, hid_report=nkro_report),
        Key( 5, key_code=0x09, hid_report=nkro_report),
        Key( 6, key_code=0x0A, hid_report=nkro_report),
        Key(12, key_code=0x0B, hid_report=nkro_report),
        Key(13, key_code=0x0C, hid_report=nkro_report),
        Key(20, key_code=0x0D, hid_report=nkro_report),
        Key(16, key_code=0x0E, hid_report=nkro_report),
        Key(26, key_code=0x0F, hid_report=nkro_report)
]

k = Keypad(keymap)
l = leds.Lights(led_map)

l.set_pixel( 0, 0xFF, 0xFF, 0xFF, 0x10)
l.set_pixel( 1, 0x00, 0x00, 0x00, 0x10)
l.set_pixel( 2, 0x00, 0x00, 0x00, 0x10)
l.set_pixel( 3, 0x00, 0x00, 0x00, 0x10)
l.set_pixel( 4, 0x00, 0x00, 0x00, 0x10)
l.set_pixel( 5, 0x00, 0x00, 0x00, 0x10)
l.set_pixel( 6, 0x00, 0x00, 0x00, 0x10)
l.set_pixel( 7, 0x00, 0x00, 0x00, 0x10)
l.set_pixel( 8, 0x00, 0x00, 0x00, 0x10)
l.set_pixel( 9, 0x00, 0x00, 0x00, 0x10)
l.set_pixel(10, 0x00, 0x00, 0x00, 0x10)
l.set_pixel(11, 0x00, 0x00, 0x00, 0x10)

l.show()

curr_led = 0;

try:
    while True:
        time.sleep(1.0)
        l.set_pixel(curr_led, 0x00, 0x00, 0x00)
        curr_led += 1
        curr_led %= 12
        l.set_pixel(curr_led, 0xFF, 0xFF, 0xFF)
        l.show()

except KeyboardInterrupt:
    pass
