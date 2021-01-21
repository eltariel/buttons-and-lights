import colorsys


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
