"""
Classes for working with lights.
"""

import atexit
from spidev import SpiDev

START_OF_FRAME = 0xE0
MAX_BRIGHTNESS = 0x1F


class Pixel:
    """
    An individual LED from a chain of APA102 LEDs
    """

    def __init__(self, n, brightness=0x00):
        """
        Constructor

        :param n: LED number. Entirely informational, is not used anywhere.
        :param brightness: initial global brightness, defaults to 0 (off). See set_brightness for additional info.
        """
        self.brightness = brightness & ~START_OF_FRAME
        self.n = n
        self.buf = bytearray([START_OF_FRAME, 0, 0, 0])

    def set(self, r, g, b, brightness=None):
        """
        Set the colour values for the pixel. All values are in the range [0x00..0xFF].

        :param r: Red value.
        :param g: Green value.
        :param b: Blue value.
        :param brightness: Optional global brightness. If None (default) uses the existing global brightness.
        """
        if brightness is not None:
            self.brightness = brightness & ~START_OF_FRAME
            self.buf[0] = START_OF_FRAME | self.brightness
        self.buf[1] = b
        self.buf[2] = g
        self.buf[3] = r

    def set_brightness(self, brightness):
        """
        Sets the global brightness.

        :param brightness:  New global brightness. Valid range is [0x00..0x1F], anything else will be truncated.
        """
        self.brightness = brightness & ~START_OF_FRAME
        self.buf[0] = START_OF_FRAME | self.brightness

    def get(self):
        """
        Gets the current RGB value of the pixel.

        :return: Tuple: (R, G, B)
        """
        return self.buf[1], self.buf[2], self.buf[3]

    def raw(self):
        """
        Gets the raw bytes to send to the LED.

        :return: 4 byte buffer.
        """
        return self.buf


class Lights:
    """
    A collection of APA102 LEDs.
    """

    def __init__(self, led_indexes):
        """
        Create the LED controller.

        :param led_indexes: physical -> logical LED mapping: led_indexes[n] = LED number
        """
        self.spi = SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 1000000

        self.pixels = [Pixel(n) for n in range(len(led_indexes))]
        self.mapping = led_indexes

        atexit.register(self._on_exit)

    def set_pixel(self, index, r, g, b, brightness=None):
        """
        Set pixel colour.

        :param index: logical index of the LED
        :param r: Red
        :param g: Green
        :param b: Blue
        :param brightness: Optional brightness value
        """
        pixel = self.get_pixel(index)
        pixel.set(r, g, b, brightness)

    def set_brightness(self, brightness, index=None):
        """
        Set global brightness.

        :param brightness: Global brightness value.
        :param index: Optional LED to address. If None, sets brightness for the whole string.
        """
        b = round(brightness)
        if index is None:
            for p in self.pixels:
                p.set_brightness(b)
        else:
            self.get_pixel(index).set_brightness(b)

    def get_pixel(self, index):
        """
        Gets the pixel at a given index.

        :param index: The index of the pixel.
        :return: The pixel.
        """
        return self.pixels[self.mapping[index]]

    def clear(self):
        """
        Blank all LEDs.
        """
        for p in self.pixels:
            p.set(0, 0, 0)

    def show(self):
        """
        Send the current pixel data to the LEDs
        """
        buf = [0x00 for _ in range(8)]
        for p in self.pixels:
            buf += p.raw()

        buf += [0xFF for _ in range(8)]
        self.spi.xfer2(buf)

    def _on_exit(self):
        self.clear()
        self.show()
