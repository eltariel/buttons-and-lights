#!/usr/bin/python3

import time
import colours
import leds

import json
import logging
import paho.mqtt.client as mqtt

from config import Configuration
from hid.usages import Keyboard
from keys import Keypad

with open("/sys/class/net/wlan0/address") as f:
    MAC_ADDR = f.read().strip().replace(":", "")

HOST = "transhouse.local"
PORT = 1883
MQTT_CLIENTID = f"keybow_{MAC_ADDR}"
MQTT_LWT_TOPIC = f"{MQTT_CLIENTID}/status"
MQTT_LWT_ALIVE = "online"
MQTT_LWT_DEAD = "offline"

HOMEASSISTANT_DEV_INFO = {
    "cns": [("mac", MAC_ADDR)],
    "ids": [MAC_ADDR],
    "mf": "Eltariel",
    "mdl": "Pimoroni Keybow + NJAK",
    "sw": "TBA",
    "name": MQTT_CLIENTID
  }

logging.basicConfig(level=logging.DEBUG)
mqttc = mqtt.Client(MQTT_CLIENTID)
mqttc.enable_logger()
mqttc.username_pw_set("mqtt", password="hassio-mqtt")
mqttc.will_set(MQTT_LWT_TOPIC, payload=MQTT_LWT_DEAD, qos=0, retain=True)
mqttc.connect(HOST, PORT, keepalive=20)
mqttc.publish(MQTT_LWT_TOPIC, payload=MQTT_LWT_ALIVE, qos=0, retain=True)

hass_discovery_topic = f"homeassistant/{{0}}/{MQTT_CLIENTID}/{{1}}/config"
light_base = f"njak/{MAC_ADDR}/light"
trigger_base = f"njak/{MAC_ADDR}/triggers"

def button_discovery_data(button_num):
  b = f"{button_num:02}"
  light_discovery_topic = hass_discovery_topic.format("light", button_num)

  light_discovery = {
    "~": f"{light_base}/{b}",
    "name": f"Keypad Light (Key {b}) @ {MAC_ADDR}",
    "unique_id": f"{MQTT_CLIENTID}_light_{button_num}",
    "cmd_t": "~/set",
    "stat_t": "~/state",
    "avty_t": MQTT_LWT_TOPIC,
    "pl_avail":MQTT_LWT_ALIVE,
    "pl_not_avail":MQTT_LWT_DEAD,
    "schema": "json",
    "brightness": True,
    "hs": True,
    "rgb": True,
    "dev": HOMEASSISTANT_DEV_INFO
  }

  trigger_discovery = [(
    hass_discovery_topic.format("device_automation", f"{b}-{trigger}"),
    {
      "automation_type": "trigger",
      "topic": f"{trigger_base}/{b}/{trigger}",
      "payload": trigger,
      "type": trigger,
      "subtype": f"button_{b}",
      "dev": HOMEASSISTANT_DEV_INFO
    }) for trigger in [
      "button_short_press",
      "button_short_release",
      "button_long_press",
      "button_long_release"
    ]]

  return [(light_discovery_topic, light_discovery)] + trigger_discovery


mqtt_meta = [button_discovery_data(b + 1) for b in range(0, 12)]
for discovery in mqtt_meta:
  for (topic, payload) in discovery:
    mqttc.publish(topic, json.dumps(payload), retain=True)
    #mqttc.publish(topic, None, retain=True)


def trigger_mqtt(button, key):
  trigger = "button_short_release"
  if button.is_held:
    trigger = "button_long_press"
  elif button.is_pressed:
    trigger = "button_short_press"

  topic = f"{trigger_base}/{key.num+1:02}/{trigger}"
  payload = trigger

  mqttc.publish(topic, payload)


class Njak:
    def __init__(self, config):
        self.config = config

        #self.keypad = Keypad(config.keymap)
        self.keys = config.keymap
        for k in self.keys:
          k.add_handler(trigger_mqtt)

        self.lights = leds.Lights(config.ledmap)
        self.lights.clear()
        self.lights.set_brightness(leds.MAX_BRIGHTNESS / 10)
        self.lights.show()

        self.cycle = colours.ColourCycler(1000, 12, 12)

        #l1 = [
        #    Keyboard.KEY_KP0,
        #    Keyboard.KEY_KPENTER,
        #    Keyboard.KEY_KP1,
        #    Keyboard.KEY_KP2,
        #    Keyboard.KEY_KP3,
        #    Keyboard.KEY_KP4,
        #    Keyboard.KEY_KP5,
        #    Keyboard.KEY_KP6,
        #    Keyboard.KEY_KP7,
        #    Keyboard.KEY_KP8,
        #    Keyboard.KEY_KP9
        #]

        #r = self.config.reports[0]
        #self.layers = [
        #    [r.key_handler(key) for key in l1],
        #    [r.key_handler(Keyboard.KEY_F13) for _ in range(11)]
        #]
        #self.keypad.add_layer(1, self.layers[0])
        #self.keypad.add_layer(2, self.layers[1])

    def loop(self):
        #time.sleep(0.01)
        mqttc.loop(timeout=0.01)
        for (i, (r, g, b)) in enumerate(self.cycle.get_step()):
            #if i == self.keypad.current_layer:
            #    self.lights.set_pixel(i, 0, 0, 0)
            #else:
            #    self.lights.set_pixel(i, r, g, b)
            self.lights.set_pixel(i, r, g, b)
        self.lights.show()
        self.cycle.next_step()


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
                new_msg = "Loop exception: {}".format(ex)
                if not new_msg == msg:
                    msg = new_msg
                    print(msg)

    except KeyboardInterrupt:
        pass
