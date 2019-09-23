#!/usr/bin/python3

import importlib
import atexit
import time
import colorsys

import hid
from keys import Key, Keypad
import leds

import behaviours
import config


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


gadget = hid.HidGadget("/dev/hidg1")
nkro_report = hid.HidBitmapReport(gadget, 1 + 31, [(0, 248, 1)])  # , report_id=1)

led_map = [l for (l, _) in config.layout]
keymap = [
    Key(pin, key_code=scancode, hid_report=nkro_report)
    for ((_, pin), scancode) in zip(config.layout, behaviours.scancodes)
]

key_pad = Keypad(keymap)
light_pad = leds.Lights(led_map)

reloading = False


def reload_config(button):
    global reloading
    if button is None or not button.is_pressed:
        print("Reload!")
        reloading = True
        importlib.reload(config)
        try:
            behaviours.init(key_pad, light_pad)
        except Exception as ex:
            print("Exception running config.init(): {}".format(ex))
        keymap[0].add_handler(reload_config)
        reloading = False


reload_config(None)

light_pad.clear()
light_pad.set_brightness(leds.MAX_BRIGHTNESS / 10)
light_pad.show()

try:
    msg = ""
    while True:
        if reloading:
            time.sleep(0.01)
        else:
            try:
                behaviours.loop(key_pad, light_pad)
            except KeyboardInterrupt:
                raise
            except Exception as ex:
                newmsg = "Loop exception: {}".format(ex)
                if not newmsg == msg:
                    msg = newmsg
                    print(msg)

except KeyboardInterrupt:
    pass
