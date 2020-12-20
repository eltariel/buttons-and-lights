"""
Classes for working with lights.
"""

import atexit
from typing import List

from spidev import SpiDev

START_OF_FRAME = 0xE0
MAX_BRIGHTNESS = 0x1F

class Pixel:
    """
    An individual LED from a chain of APA102 LEDs
    """

    PIXEL_OFF = bytearray([START_OF_FRAME, 0, 0, 0])


    def __init__(self, pin, brightness=0x00):
        """
        Constructor

        :param pin: 'Pin' number for the LED, i.e. it's physical position in the LED string.
        :param brightness: initial global brightness, defaults to 0 (off). See set_brightness for additional info.
        """
        self.brightness = brightness & ~START_OF_FRAME
        self._pin = pin
        self.buf = bytearray([START_OF_FRAME, 0xFF, 0xFF, 0xFF])
        self.on = False

    @property
    def pin(self) -> int:
        """
        Returns the 'pin' number for the LED, i.e. it's physical position in the LED string.
        """
        return self._pin

    def turn_off(self):
        """
        Turns off the LED while leaving the brightness alone.
        """
        self.on = False

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
            self.on = self.brightness > 0
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
        Gets the current RGB value and brightness of the pixel.

        :return: Tuple: (R, G, B, brightness)
        """
        return self.buf[3], self.buf[2], self.buf[1], self.brightness

    def raw(self):
        """
        Gets the raw bytes to send to the LED.

        :return: 4 byte buffer.
        """
        return self.buf if self.on else Pixel.PIXEL_OFF


class Lights:
    """
    A collection of APA102 LEDs.
    """

    def __init__(self, pixels: List[Pixel]):
        """
        Create the LED controller.

        :param pixels: List of Pixels in logical (key number) order.
        """
        self.spi = SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 1000000

        self.pixels_logical = pixels
        self.pixels_physical = sorted(pixels, key=lambda x: x.pin)

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
        self.pixels_logical[index].set(r, g, b, brightness)

    def set_brightness(self, brightness, index=None):
        """
        Set global brightness.

        :param brightness: Global brightness value.
        :param index: Optional LED to address. If None, sets brightness for the whole string.
        """
        b = round(brightness)
        if index is None:
            for p in self.pixels_logical:
                p.set_brightness(b)
        else:
            self.pixels_logical[index].set_brightness(b)

    def get_pixel(self, index):
        """
        Gets the pixel at a given index.

        :param index: The index (1-based) of the pixel.
        :return: The pixel.
        """
        return self.pixels_logical[index - 1]

    def clear(self):
        """
        Blank all LEDs.
        """
        for p in self.pixels_logical:
            #p.set(0, 0, 0)
            p.turn_off()

    def show(self):
        """
        Send the current pixel data to the LEDs
        """
        buf = [0x00 for _ in range(8)]
        for p in self.pixels_physical:
            buf += p.raw()

        buf += [0xFF for _ in range(8)]
        self.spi.xfer2(buf)

    def _on_exit(self):
        self.clear()
        self.show()
