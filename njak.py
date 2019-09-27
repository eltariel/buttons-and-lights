#!/usr/bin/python3

import importlib
import atexit
import time
import colorsys

import hid
from keys import Key, Keypad
import leds

import behaviours
from config import Configuration


def key_int_handler(keynum):
    def h(button):
        if button.is_held:
            print("Button {} held".format(keynum))
        elif button.is_pressed:
            print("Button {} pressed".format(keynum))
        else:
            print("Button {} released".format(keynum))

    return h


keycodes = {
    "A": 0x04,
    "B": 0x05,
    "C": 0x06,
    "D": 0x07,
    "E": 0x08,
    "F": 0x09,
    "G": 0x0A,
    "H": 0x0B,
    "I": 0x0C,
    "J": 0x0D,
    "K": 0x0E,
    "L": 0x0F,
    "M": 0x10,
    "N": 0x11,
    "O": 0x12,
    "P": 0x13,
    "Q": 0x14,
    "R": 0x15,
    "S": 0x16,
    "T": 0x17,
    "U": 0x18,
    "V": 0x19,
    "W": 0x1A,
    "X": 0x1B,
    "Y": 0x1C,
    "Z": 0x1D,
    "1": 0x1E,
    "2": 0x1F,
    "3": 0x20,
    "4": 0x21,
    "5": 0x22,
    "6": 0x23,
    "7": 0x24,
    "8": 0x25,
    "9": 0x26,
    "0": 0x27,
    "LEFTSHIFT": 0xE1,
}


def type_string(word, report):
    def h(button):
        if not button.is_pressed:
            for c in word:
                keycode = keycodes[c.upper()]
                if c.isupper():
                    report.press(keycodes["LEFTSHIFT"])
                    report.send()
                report.press(keycode)
                report.send()
                if c.isupper():
                    report.release(keycodes["LEFTSHIFT"])
                report.release(keycode)
                report.send()

    return h


class Njak:
    def __init__(self, config):
        self._reloading = False
        self.config = config

        self.keypad = Keypad(config.keymap)
        self.lightpad = leds.Lights(config.ledmap)

        self.lightpad.clear()
        self.lightpad.set_brightness(leds.MAX_BRIGHTNESS / 10)
        self.lightpad.show()

        self.behaviour = behaviours.Behaviour(self)

    def loop(self):
        if self._reloading:
            time.sleep(0.01)
        else:
            self.behaviour.loop()

    def reload(self, *args, **kwargs):
        print("Reload!")
        self._reloading = True
        importlib.reload(behaviours)
        try:
            self.behaviour = behaviours.Behaviour(self)
        except Exception as ex:
            print("Exception running config.init(): {}".format(ex))
        self.keypad.add_handler(0, self.reload)
        self._reloading = False


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
                newmsg = "Loop exception: {}".format(ex)
                if not newmsg == msg:
                    msg = newmsg
                    print(msg)

    except KeyboardInterrupt:
        pass
