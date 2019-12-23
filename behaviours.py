import time
import colorsys

import leds
from hid_usages import Keyboard


class ColourCycler:
    def __init__(self, steps, leds, lit):
        self.steps = steps
        self.colours = [
            (round(r * 0xFF), round(g * 0xFF), round(b * 0xFF))
            for (r, g, b) in [
                colorsys.hsv_to_rgb(x / steps, 1, 1) for x in range(steps)
            ]
        ]

        self.curr_step = 0
        self.led_count = leds
        self.lit_count = lit

    def get_step(self):
        return [
            self.colours[
                (self.curr_step - (i * self.steps // self.led_count)) % self.steps
            ]
            for i in range(0, self.led_count)
        ]

    def next_step(self):
        self.curr_step += 1
        self.curr_step %= self.steps


class Behaviour:
    def __init__(self, host):
        self.host = host

        self.host.lightpad.clear()
        self.host.lightpad.set_brightness(leds.MAX_BRIGHTNESS / 10)
        self.host.lightpad.show()
        
        self.cycle = ColourCycler(1000, 12, 12)

        r = self.host.config.reports[0]
        self.layers = [
            [
                r.key_handler(Keyboard.KEY_KP0),
                r.key_handler(Keyboard.KEY_KPENTER),
                r.key_handler(Keyboard.KEY_KP1),
                r.key_handler(Keyboard.KEY_KP2),
                r.key_handler(Keyboard.KEY_KP3),
                r.key_handler(Keyboard.KEY_KP4),
                r.key_handler(Keyboard.KEY_KP5),
                r.key_handler(Keyboard.KEY_KP6),
                r.key_handler(Keyboard.KEY_KP7),
                r.key_handler(Keyboard.KEY_KP8),
                r.key_handler(Keyboard.KEY_KP9),
            ],
            [r.key_handler(Keyboard.KEY_F13) for _ in range(11)]
        ]
        self.host.keypad.add_layers(self.layers)

        #for (i, handler) in enumerate(self.layers[0]):
        #    if handler is not None:
        #        self.host.keypad.add_handler(i + 1, 0, handler)

    def loop(self):
        time.sleep(0.01)
        for (i, (r, g, b)) in enumerate(self.cycle.get_step()):
            self.host.lightpad.set_pixel(i, r, g, b)
        self.host.lightpad.show()
        self.cycle.next_step()
