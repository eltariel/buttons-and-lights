#!/usr/bin/python3

import time
import colours
import leds
from config import Configuration
from hid.usages import Keyboard
from keys import Keypad


class Njak:
    def __init__(self, config):
        self.config = config

        self.keypad = Keypad(config.keymap)
        self.lights = leds.Lights(config.ledmap)

        self.lights.clear()
        self.lights.set_brightness(leds.MAX_BRIGHTNESS / 10)
        self.lights.show()

        self.cycle = colours.ColourCycler(1000, 12, 12)

        l1 = [
            Keyboard.KEY_KP0,
            Keyboard.KEY_KPENTER,
            Keyboard.KEY_KP1,
            Keyboard.KEY_KP2,
            Keyboard.KEY_KP3,
            Keyboard.KEY_KP4,
            Keyboard.KEY_KP5,
            Keyboard.KEY_KP6,
            Keyboard.KEY_KP7,
            Keyboard.KEY_KP8,
            Keyboard.KEY_KP9
        ]

        r = self.config.reports[0]
        self.layers = [
            [r.key_handler(key) for key in l1],
            [r.key_handler(Keyboard.KEY_F13) for _ in range(11)]
        ]
        self.keypad.add_layer(1, self.layers[0])
        self.keypad.add_layer(2, self.layers[1])

    def loop(self):
        time.sleep(0.01)
        for (i, (r, g, b)) in enumerate(self.cycle.get_step()):
            if i == self.keypad.current_layer:
                self.lights.set_pixel(i, 0, 0, 0)
            else:
                self.lights.set_pixel(i, r, g, b)
        self.lights.show()
        self.cycle.next_step()


if __name__ == '__main__':
    c = Configuration()
    n = Njak(c)

    try:
        msg = ""
        while True:
            try:
                n.loop()
            except KeyboardInterrupt:
                raise
            except Exception as ex:
                new_msg = "Loop exception: {}".format(ex)
                if not new_msg == msg:
                    msg = new_msg
                    print(msg)

    except KeyboardInterrupt:
        pass
