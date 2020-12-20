"""
IO Mapping for buttons and lights.

Options:
    layout: list of (led position, gpio pin) for each key. io_mapping[n] represents the nth key.
"""
from dataclasses import dataclass

from hardware.keys import Key
from hardware.leds import Pixel, Lights

from mqtt.mqtt_config import MqttConfig

import socket
import json


HOST_NAME = socket.gethostname()
mc = MqttConfig.read("njak-mqtt.json")


@dataclass
class KeyCfg:
    key_number: int
    led_position: int
    key_pin: int

    @property
    def key(self) -> Key:
        return Key(self.key_number, self.key_pin)

    @property
    def pixel(self) -> Pixel:
        return Pixel(self.led_position)


layout = [
    KeyCfg(1, 3, 17),
    KeyCfg(2, 7, 27),
    KeyCfg(3, 11, 23),
    KeyCfg(4, 2, 22),
    KeyCfg(5, 6, 24),
    KeyCfg(6, 10, 5),
    KeyCfg(7, 1, 6),
    KeyCfg(8, 5, 12),
    KeyCfg(9, 9, 13),
    KeyCfg(10, 0, 20),
    KeyCfg(11, 4, 16),
    KeyCfg(12, 8, 26),
]


class Configuration:
    def __init__(self):
        self.layout = layout
        self.lights = Lights([k.pixel for k in layout])
        self.keys = [k.key for k in self.layout]
