#!/usr/bin/python3

import atexit
import time
import colorsys

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
nkro_report = hid.HidBitmapReport(gadget, 1+31, [(0, 248, 1)])  # , report_id=1)

led_map = [3, 7, 11, 2, 6, 10, 1, 5, 9, 0, 4, 8]
keymap = [
        Key(17, key_code=0x04, hid_report=nkro_report),
        Key(27, key_code=0x05, hid_report=nkro_report, handler=key_int_handler(1)),
        Key(23, key_code=0x06, hid_report=nkro_report),
        Key(22, key_code=0x07, hid_report=nkro_report),
        Key(24, key_code=0x08, hid_report=nkro_report),
        Key(5,  key_code=0x09, hid_report=nkro_report),
        Key(6,  key_code=0x0A, hid_report=nkro_report),
        Key(12, key_code=0x0B, hid_report=nkro_report),
        Key(13, key_code=0x0C, hid_report=nkro_report),
        Key(20, key_code=0x0D, hid_report=nkro_report),
        Key(16, key_code=0x0E, hid_report=nkro_report),
        Key(26, key_code=0x0F, hid_report=nkro_report)
]

key_pad = Keypad(keymap)
light_pad = leds.Lights(led_map)

steps = 1000
colours = [(round(r*0xFF), round(g*0xFF), round(b*0xFF))
           for (r, g, b)
           in [colorsys.hsv_to_rgb(x/steps, 1, 1) for x in range(steps)]]

light_pad.clear()
light_pad.set_brightness(leds.MAX_BRIGHTNESS >> 2)
light_pad.show()

curr_step = 0
led_count = len(led_map)

try:
    while True:
        time.sleep(0.01)
        for i in range(0, led_count):
            (r, g, b) = colours[(curr_step - (i * steps // led_count)) % steps]
            light_pad.set_pixel(i, r, g, b)
        light_pad.show()
        curr_step += 1
        curr_step %= steps

except KeyboardInterrupt:
    pass
