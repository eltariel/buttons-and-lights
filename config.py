"""
IO Mapping for buttons and lights.

Options:
    layout: list of (led position, gpio pin) for each key. io_mapping[n] represents the nth key.
"""

from hid.bitmap_report import *
from hid.gadget import *
import keys
from keys import Key
import leds


layout = [
    (3, 17),
    (7, 27),
    (11, 23),
    (2, 22),
    (6, 24),
    (10, 5),
    (1, 6),
    (5, 12),
    (9, 13),
    (0, 20),
    (4, 16),
    (8, 26),
]


class Configuration:
    def __init__(self):
        self.layout = layout
        self.gadget = HidGadget("/dev/hidg1")
        self.reports = [BitmapReport(self.gadget, 32, [(0, 248, 1)])]

        self.ledmap = [l for (l, _) in self.layout]
        self.keymap = [Key(i, pin)
                for (i, (_, pin))
                in enumerate(self.layout)]
