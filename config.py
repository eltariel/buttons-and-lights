"""
IO Mapping for buttons and lights.

Options:
    layout: list of (led position, gpio pin) for each key. io_mapping[n] represents the nth key.
"""

import hid
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
        self.gadget = hid.HidGadget("/dev/hidg1")
        self.reports = [hid.HidBitmapReport(self.gadget, 32, [(0, 248, 1)])]

        self.ledmap = [l for (l, _) in self.layout]
        self.keymap = [Key(i, pin, hid_report=self.reports[0])
                for (i, (_, pin))
                in enumerate(self.layout)]
