#!/usr/bin/python3

import time
import math
from typing import List

import colours
from hardware import leds

import json
import logging
import paho.mqtt.client as mqtt

from dataclasses import asdict, astuple, is_dataclass

from config import Configuration, HOST_NAME, mc
from hass.mqtt_light import MqttLight, LightState, RGBColor
from hass.mqtt_trigger import MqttTrigger
from mqtt.mqtt_config import MqttConfig


logging.basicConfig(level=logging.DEBUG)

def on_connect(client, userdata, flags, rc):
  mqttc.publish(mc.lwt.topic, payload=mc.lwt.alive, qos=0, retain=True)


def on_message(client, userdata, msg):
  print(msg.topic+" "+str(msg.payload))


mqttc = mqtt.Client(mc.client_id)
#mqttc.enable_logger()
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.username_pw_set(mc.user, password=mc.password)
mqttc.will_set(mc.lwt.topic, payload=mc.lwt.dead, qos=0, retain=True)
mqttc.connect(mc.host, mc.port, keepalive=20)


class Discovery:
  trigger_types = [
    "button_short_press",
    "button_short_release",
    "button_long_press",
    "button_long_release",
    ]


class LedKey:
  def __init__(self, key, light, triggers):
    self._log = logging.getLogger(type(self).__name__)
    self._key = key
    self._light = light
    self._triggers = {t.trigger_type: t for t in triggers}
    
    self._key.add_handler(self._handle_key)
    self._light.state = LightState(True, 128, RGBColor(0, 0, 0))

    self._light.listen()

  def publish_state(self):
    self._light.publish_state()

  def set_color(self, r, g, b):
    self._light.set_color(r, g, b)

  def _handle_key(self, button, key):
    trigger = "button_short_release"
    if button.is_held:
      trigger = "button_long_press"
    elif button.is_pressed:
      trigger = "button_short_press"
    
    self._triggers[trigger].trigger()


class Njak:
  def __init__(self, config: Configuration):
    self.config = config

    self.keys = config.keys
    self.lights = config.lights

    self.lights.clear()
    self.lights.set_brightness(leds.MAX_BRIGHTNESS / 10)
    self.lights.show()

    self.mqtt_keys = []
    for key in self.keys:
      pixel = self.lights.get_pixel(key.num)

      light = MqttLight(key.num, pixel, mqttc)
      triggers: List[MqttTrigger] = [MqttTrigger(key.num, t, mqttc) for t in Discovery.trigger_types]

      for d in [light] + triggers:
        d.publish()

      self.mqtt_keys += [LedKey(key, light, triggers)]

    self.cycle = colours.ColourCycler(1000, 12, 12)
    self.loop_ctr = 0

  def loop(self):
    time.sleep(0.01)
    for (i, (r, g, b)) in enumerate(self.cycle.get_step()):
      self.mqtt_keys[i].set_color(r, g, b)
      if not self.loop_ctr:
        self.mqtt_keys[i].publish_state()
    self.lights.show()
    self.cycle.next_step()

    self.loop_ctr = (self.loop_ctr + 1) % 100


if __name__ == '__main__':
  cfg = Configuration()
  n = Njak(cfg)

  mqttc.loop_start()

  try:
    msg = ""
    while True:
      try:
        n.loop()
      except KeyboardInterrupt:
        raise
      except Exception as ex:
        new_msg = "Loop exception: {}".format(ex)
        if not new_msg == msg:
          msg = new_msg
          print(msg)

  except KeyboardInterrupt:
    pass
  mqttc.loop_stop()
