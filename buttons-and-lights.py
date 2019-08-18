#!/usr/bin/python3

import atexit
import time

import hid
import keys
import leds

gadget = hid.HidGadget('/dev/hidg1')
nkro_report = hid.HidBitmapReport(gadget, 1+31)#, report_id=1)

keymap = [
        {'gpio':17, 'led':3 , 'key_code':0x04, 'hid_report':nkro_report},
        {'gpio':27, 'led':7 , 'key_code':0x05, 'hid_report':nkro_report, 'handler':None },
        {'gpio':23, 'led':11, 'key_code':0x06, 'hid_report':nkro_report},
        {'gpio':22, 'led':2 , 'key_code':0x07, 'hid_report':nkro_report},
        {'gpio':24, 'led':6 , 'key_code':0x08, 'hid_report':nkro_report},
        {'gpio': 5, 'led':10, 'key_code':0x09, 'hid_report':nkro_report},
        {'gpio': 6, 'led':1 , 'key_code':0x0A, 'hid_report':nkro_report},
        {'gpio':12, 'led':5 , 'key_code':0x0B, 'hid_report':nkro_report},
        {'gpio':13, 'led':9 , 'key_code':0x0C, 'hid_report':nkro_report},
        {'gpio':20, 'led':0 , 'key_code':0x0D, 'hid_report':nkro_report},
        {'gpio':16, 'led':4 , 'key_code':0x0E, 'hid_report':nkro_report},
        {'gpio':26, 'led':8 , 'key_code':0x0F, 'hid_report':nkro_report}
]


def key_int_handler(keynum):
    def h(button):
        if button.is_held:
            print("Button {} held".format(keynum))
        elif button.is_pressed:
            print("Button {} pressed".format(keynum))
        else:
            print("Button {} released".format(keynum))
    return h

k = keys.Keypad(keymap)
k.add_handler(0, key_int_handler(0))
k.add_handler(1, key_int_handler(1))
k.add_handler(2, key_int_handler(2))
k.add_handler(3, key_int_handler(3))
k.add_handler(4, key_int_handler(4))
k.add_handler(5, key_int_handler(5))
k.add_handler(6, key_int_handler(6))
k.add_handler(7, key_int_handler(7))
k.add_handler(8, key_int_handler(8))
k.add_handler(9, key_int_handler(9))
k.add_handler(10, key_int_handler(10))
k.add_handler(11, key_int_handler(11))

l = leds.Lights(keymap)
l.set_pixel( 0, 0xFF, 0xFF, 0xFF)
l.set_pixel( 1, 0x00, 0x00, 0x00)
l.set_pixel( 2, 0x00, 0x00, 0x00)
l.set_pixel( 3, 0x00, 0x00, 0x00)
l.set_pixel( 4, 0x00, 0x00, 0x00)
l.set_pixel( 5, 0x00, 0x00, 0x00)
l.set_pixel( 6, 0x00, 0x00, 0x00)
l.set_pixel( 7, 0x00, 0x00, 0x00)
l.set_pixel( 8, 0x00, 0x00, 0x00)
l.set_pixel( 9, 0x00, 0x00, 0x00)
l.set_pixel(10, 0x00, 0x00, 0x00)
l.set_pixel(11, 0x00, 0x00, 0x00)

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
