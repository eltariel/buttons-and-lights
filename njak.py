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
        self.keypad.add_handler(0, 0, self.reload)
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
