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
MQTT_USER = "mqtt"
MQTT_PASS = "hassio-mqtt"

MQTT_CLIENTID = f"keybow_{MAC_ADDR}"
MQTT_LWT_TOPIC = f"{MQTT_CLIENTID}/status"
MQTT_LWT_ALIVE = "online"
MQTT_LWT_DEAD = "offline"

hass_discovery_topic = f"homeassistant/{{0}}/{MQTT_CLIENTID}/{{1}}/config"
light_base = f"njak/{MAC_ADDR}/light"
trigger_base = f"njak/{MAC_ADDR}/triggers"

HOMEASSISTANT_DEV_INFO = {
    "cns": [("mac", MAC_ADDR)],
    "ids": [MAC_ADDR],
    "mf": "Eltariel",
    "mdl": "Pimoroni Keybow + NJAK",
    "sw": "TBA",
    "name": MQTT_CLIENTID
    }

logging.basicConfig(level=logging.DEBUG)

def on_connect(client, userdata, flags, rc):
  mqttc.subscribe(f"{light_base}/#")
  mqttc.publish(MQTT_LWT_TOPIC, payload=MQTT_LWT_ALIVE, qos=0, retain=True)


def on_message(client, userdata, msg):
  print(msg.topic+" "+str(msg.payload))


mqttc = mqtt.Client(MQTT_CLIENTID)
mqttc.enable_logger()
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.username_pw_set(MQTT_USER, password=MQTT_PASS)
mqttc.will_set(MQTT_LWT_TOPIC, payload=MQTT_LWT_DEAD, qos=0, retain=True)
mqttc.connect(HOST, PORT, keepalive=20)

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
      "pl_avail": MQTT_LWT_ALIVE,
      "pl_not_avail": MQTT_LWT_DEAD,
      "schema": "json",
      "brightness": True,
      "brightness_scale": leds.MAX_BRIGHTNESS,
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
    }
  ) for trigger in [
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


class MqttLedKey:
  def __init__(self, config, key, lights, mqtt_client):
    self.config = config
    self.key = key
    self.lights = lights
    self.client = mqtt_client
    self.state_topic = f"{light_base}/{key.num+1:02}/state"
    self.command_topic = f"{light_base}/{key.num+1:02}/set"
    self.trigger_topic = f"{trigger_base}/{key.num+1:02}"
    
    self.key.add_handler(self._handle_key)
    self.client.message_callback_add(self.command_topic, self._handle_message)
    self.publish_state()

  def publish_state(self):
    pixel = self.lights.get_pixel(self.key.num)
    (r, g, b, br) = pixel.get()

    payload = {
        "brightness": br << 3,
        "color": {
          "r": r,
          "g": g,
          "b": b,
        },
        "state": "OFF" if not pixel.on else "ON",
      }
    self.client.publish(self.state_topic, json.dumps(payload), retain=True)

  def _handle_message(self, client, userdata, message):
    p = json.loads(message.payload)
    print(f"Light command for LED {self.key.num+1:02}: {p}")

    pixel = self.lights.get_pixel(self.key.num)
    (r, g, b, br) = pixel.get()

    br = p.get("brightness")
    if br is not None:
      br = br >> 3

    st = p.get("state", "OFF")

    if st == "OFF":
      pixel.turn_off()
    else:
      color = p.get("color")
      if color is not None:
        r = color.get("r", r)
        g = color.get("g", g)
        b = color.get("b", b)

      pixel.set(r, g, b, br)
    self.publish_state()

  def _handle_key(self, button, key):
    trigger = "button_short_release"
    if button.is_held:
      trigger = "button_long_press"
    elif button.is_pressed:
      trigger = "button_short_press"

    self.client.publish(f"{self.trigger_topic}/{trigger}", payload=trigger)


class Njak:
  def __init__(self, config):
    self.config = config

    self.keys = config.keymap

    self.lights = leds.Lights(config.ledmap)
    self.lights.clear()
    self.lights.set_brightness(leds.MAX_BRIGHTNESS / 10)
    self.lights.show()

    self.mqtt_keys = [MqttLedKey(config, k, self.lights, mqttc) for k in self.keys]

    self.cycle = colours.ColourCycler(1000, 12, 12)

  def loop(self):
    time.sleep(0.01)
    for (i, (r, g, b)) in enumerate(self.cycle.get_step()):
      self.lights.set_pixel(i, r, g, b)
    self.lights.show()
    self.cycle.next_step()


if __name__ == '__main__':
  c = Configuration()
  n = Njak(c)

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
