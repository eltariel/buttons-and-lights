import time
import colorsys

import leds
from hid_usages import Keyboard

# NOTE: This is upside down!
scancodes = [
    None,
    Keyboard.KEY_F13,
    Keyboard.KEY_F13,
    Keyboard.KEY_F13,
    Keyboard.KEY_F13,
    Keyboard.KEY_F13,
    Keyboard.KEY_F13,
    Keyboard.KEY_F13,
    Keyboard.KEY_F13,
    Keyboard.KEY_F13,
    Keyboard.KEY_F13,
    Keyboard.KEY_F13,
]


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


cycle = ColourCycler(500, 12, 12)


def init(key_pad, light_pad):
    global cycle
    light_pad.clear()
    light_pad.set_brightness(leds.MAX_BRIGHTNESS / 10)
    light_pad.show()


def loop(key_pad, light_pad):
    time.sleep(0.01)
    for (i, (r, g, b)) in enumerate(cycle.get_step()):
        light_pad.set_pixel(i, r, g, b)
    light_pad.show()
    cycle.next_step()
