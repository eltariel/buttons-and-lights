#!/usr/bin/env python3

import atexit
import time
from spidev import SpiDev
from gpiozero import Button


START_OF_FRAME = 0xE0

class Pixel:
    def __init__(self, n):
        #self.brightness = 0x1F
        self.brightness = 0x03
        self.n = n
        self.buf = [START_OF_FRAME | self.brightness, 0, 0, 0]

    def set(self, r, g, b):
        self.buf = [START_OF_FRAME | self.brightness, b, g, r]

    def get(self):
        return (self.buf[1], self.buf[2], self.buf[3])

    def raw(self):
        return self.buf

class Lights:
    def __init__(self, keymap):
        self.spi = SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 1000000

        self.pixels = [Pixel(n) for n in range(len(keymap))]
        self.mapping = [k['led'] for k in keymap]

        atexit.register(self._on_exit)

    def set_pixel(self, index, r, g, b):
        pixel = self.pixels[self.mapping[index]]
        pixel.set(r, g, b);

    def clear(self):
        for p in self.pixels:
            p.set(0, 0, 0)

    def show(self):
        buf = [0x00 for _ in range(8)]
        for p in self.pixels:
            buf += p.raw()

        buf += [0xFF for _ in range(8)]
        self.spi.xfer2(buf)

    def _on_exit(self):
        self.clear()
        self.show()


class Key:
    def __init__(self, pin):
        self.button = Button(pin)
        self.button.when_pressed = self._handler
        self.button.when_released = self._handler
        self.button.when_held = self._handler
        
        self.handlers = []

    def add_handler(self, handler):
        self.handlers.append(handler)

    def _handler(self, button):
        for h in self.handlers:
            h(button)

            
class Keypad:
    def __init__(self, keymap):
        self.keys = [Key(k['gpio']) for k in keymap]

    def add_handler(self, key, handler):
        self.keys[key].add_handler(handler)

keymap = [
        {'gpio':17, 'led':3, 'key_code':None, 'handler':None},
        {'gpio':27, 'led':7 },
        {'gpio':23, 'led':11},
        {'gpio':22, 'led':2 },
        {'gpio':24, 'led':6 },
        {'gpio': 5, 'led':10},
        {'gpio': 6, 'led':1 },
        {'gpio':12, 'led':5 },
        {'gpio':13, 'led':9 },
        {'gpio':20, 'led':0 },
        {'gpio':16, 'led':4 },
        {'gpio':26, 'led':8 }
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

k = Keypad(keymap)
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

l = Lights(keymap)
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
