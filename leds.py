import atexit
from spidev import SpiDev

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


