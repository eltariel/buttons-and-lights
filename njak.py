#!/usr/bin/python3

import time
import colours
import leds

import json
import logging
import socket
import paho.mqtt.client as mqtt

from dataclasses import dataclass, asdict
from typing import Tuple, List, Dict, Any

from config import Configuration
from hid.usages import Keyboard
from keys import Keypad


with open("/sys/class/net/wlan0/address") as f:
  MAC_ADDR = f.read().strip().replace(":", "")

HOST_NAME = socket.gethostname()

MQTT_HOST = "transhouse.local"
MQTT_PORT = 1883
MQTT_USER = "mqtt"
MQTT_PASS = "hassio-mqtt"

MQTT_CLIENTID = f"njak_{MAC_ADDR}"
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
    "name": f"Keybow {HOST_NAME}"
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
mqttc.connect(MQTT_HOST, MQTT_PORT, keepalive=20)


class MqttKeyInfo:
  def __init__(self, button: int):
    self._button = button
    self._button_str = f"{button:02}"

  @property
  def button(self):
    return self._button

  @property
  def button_str(self):
    return self._button_str

  @property
  def light_discovery_topic(self):
    return self._discovery_topic("light", self.button_str)

  def trigger_discovery_topic(self, trigger):
    return self._discovery_topic("device_automation", f"{self.button_str}_{trigger}")

  @property
  def light_topic(self):
    return self._target_topic(f"light/{self.button_str}")

  def trigger_topic_for(self, trigger):
    return self._target_topic(f"trigger/{self.button_str}/{trigger}")

  def payload_for(self, trigger):
    return f"{self.button}:{trigger}"

  def _target_topic(self, component_id):
    return f"njak/{MAC_ADDR}/{component_id}"

  def _discovery_topic(self, component_id, object_id):
    return f"homeassistant/{component_id}/{MQTT_CLIENTID}/{object_id}/config"


class Discoverable:
  DEVICE_ROOT = f"njak"
  DISCOVERY_ROOT = f"homeassistant"

  def __init__(self, mqtt_client: mqtt.Client):
    self._client = mqtt_client
    self._log = logging.getLogger(type(self).__name__)

  def publish(self):
    self._log.debug(f"  PUBLISH {self.discovery_topic} --> {json.dumps(self.discovery_payload, indent=2)}")
    self._client.publish(self.discovery_topic, json.dumps(self.discovery_payload), retain=True)

  def unpublish(self):
    self._log.debug(f"  UNPUBLISH {self.discovery_topic}")
    self._client.publish(self.discovery_topic, None)

  def _topic(self, component_id: str) -> str:
    return f"{self.DEVICE_ROOT}/{MAC_ADDR}/{component_id}"

  def _discovery_topic(self, component_id: str, object_id: str) -> str:
    return f"{self.DISCOVERY_ROOT}/{component_id}/{MQTT_CLIENTID}/{object_id}/config"


class MqttTrigger(Discoverable):
  def __init__(self, button: int, trigger_type: str, mqtt_client: mqtt.Client):
    super().__init__(mqtt_client)
    self._button = button
    self._btn_str = f"{button:02}"
    self._type = trigger_type
    self._subtype = f"button_{self._btn_str}"

  @property
  def trigger_type(self) -> str:
    return self._type

  @property
  def topic(self) -> str:
    return self._topic(f"trigger/{self._btn_str}/{self._type}")

  @property
  def payload(self) -> str:
    return f"{self._button}:{self._type}"
    return self.payload_for(self._type)

  @property
  def discovery_topic(self) -> str:
    return self._discovery_topic("device_automation", f"{self._btn_str}_{self._type}")

  @property
  def discovery_payload(self) -> Dict[str, Any]:
    return {
          "automation_type": "trigger",
          "topic": self.topic,
          "payload": self.payload,
          "type": self._type,
          "subtype": self._subtype,
          "dev": HOMEASSISTANT_DEV_INFO
          }

  def trigger(self):
    self._log.debug(f"  {self.topic} TRIGGER --> {self.payload}")
    self._client.publish(self.topic, self.payload)


@dataclass
class RGBColor:
  r: int
  g: int
  b: int


@dataclass
class LightState:
  on: bool = None
  brightness: int = None
  color: RGBColor = None

  def to_payload(self) -> str:
    return json.dumps({
        "brightness": self.brightness,
        "color": asdict(self.color),
        "state": "OFF" if not self.on else "ON",
      })


class MqttLight(Discoverable):
  def __init__(self, button, mqtt_client):
    super().__init__(mqtt_client)
    self._button = button
    self._btn_str = f"{button:02}"
    self._light_topic = self._topic(f"light/{self._btn_str}")
    self._state = LightState(False, 0, RGBColor(0, 0, 0))
    self._listeners = []

  @property
  def state_topic(self):
    return f"{self._light_topic}/state"

  @property
  def listen_topic(self):
    return f"{self._light_topic}/set"

  @property
  def state(self) -> LightState:
    return self._state

  @state.setter
  def state(self, value: LightState):
    self._state = value
    for l in self._listeners:
      l(self)

    self.publish_state()

  def set(self, on: bool, brightness: int, color: RGBColor):
    self.state = LightState(on, brightness, color)

  @property
  def discovery_topic(self):
    return self._discovery_topic("light", self._btn_str)

  @property
  def discovery_payload(self):
    return {
      "~": self._light_topic,
      "name": f"Key LED {self._btn_str} @ Keybow {HOST_NAME}",
      "unique_id": f"Keybow_{HOST_NAME}_light_{self._btn_str}",
      "cmd_t": "~/set",
      "stat_t": "~/state",
      "avty_t": MQTT_LWT_TOPIC,
      "pl_avail": MQTT_LWT_ALIVE,
      "pl_not_avail": MQTT_LWT_DEAD,
      "schema": "json",
      "brightness": True,
      "hs": True,
      "rgb": True,
      "dev": HOMEASSISTANT_DEV_INFO
      }

  def publish_state(self):
    p = self.state.to_payload()
    self._log.debug(f"  {self.state_topic} STATE --> {p}")
    self._client.publish(self.state_topic, self._state.to_payload())

  def add_listener(self, listener):
    self._log.debug(f"Adding listener: {listener}")
    self._listeners += [listener]

  def listen(self):
    self._log.debug(f"Listening on {self.listen_topic}")
    self._client.message_callback_add(self.listen_topic, self._handle_message)

  def _handle_message(self):
    """
    Expects JSON to look like this, potentially with fields omitted:
    {
        "brightness": 255,
        "color": {
          "r": 255,
          "g": 180,
          "b": 200,
        },
        "state": "ON",
    }
    """
    p = json.loads(message.payload)
    self._log.debug(f"Light command for LED {self._btn_str}: {p}")

    br = p.get("brightness", self._state.brightness)

    st = p.get("state")
    on = st == "ON" if st is not None else self._state.on
    
    curr_color = self._state.color
    c = p.get("color")
    if c is not None:
      r = c.get("r", curr_color.r)
      g = c.get("g", curr_color.g)
      b = c.get("b", curr_color.b)
      color = RGBColor(r, g, b)
    else:
      color = curr_color

    self.state = LightState(on, br, color)
    for l in self._listeners:
      l(self)

    self.update_state(on, br, color)


class Discovery:
  trigger_types = [
    "button_short_press",
    "button_short_release",
    "button_long_press",
    "button_long_release",
    ]


class LedKey:
  def __init__(self, key, pixel, light, triggers):
    self._key = key
    self._pixel = pixel
    self._light = light
    self._triggers = {t.trigger_type: t for t in triggers}
    
    self._key.add_handler(self._handle_key)
    self._light.add_listener(self._handle_light)
    self.publish_state()

    self._light.listen()

  def publish_state(self):
    self._light.publish_state()

  def set_color(self, r, g, b):
    self._light.state = LightState(self._light.state.on, self._light.state.brightness, RGBColor(r, g, b))

  def _handle_light(self, light: MqttLight):
    state = light.state

    br = state.brightness >> 3 # TODO: Make this stay on for low values
    r, g, b = state.color

    if state.on:
      self._pixel.set(r, g, b, br)
    else:
      self._pixel.turn_off()


  def _handle_message(self, client, userdata, message):
    p = json.loads(message.payload)
    print(f"Light command for LED {self.key.num+1:02}: {p}")

    (r, g, b, br) = self._pixel.get()

    br = p.get("brightness")
    if br is not None:
      br = br >> 3

    st = p.get("state", "OFF")

    if st == "OFF":
      self._pixel.turn_off()
    else:
      color = p.get("color")
      if color is not None:
        r = color.get("r", r)
        g = color.get("g", g)
        b = color.get("b", b)

      self._pixel.set(r, g, b, br)
    self.publish_state()

  def _handle_key(self, button, key):
    trigger = "button_short_release"
    if button.is_held:
      trigger = "button_long_press"
    elif button.is_pressed:
      trigger = "button_short_press"
    
    self._triggers[trigger].trigger()

class Njak:
  def __init__(self, config):
    self.config = config

    self.keys = config.keymap

    self.lights = leds.Lights(config.ledmap)
    self.lights.clear()
    self.lights.set_brightness(leds.MAX_BRIGHTNESS / 10)
    self.lights.show()
    self.mqtt_keys = []

    for k in self.keys:
      light = MqttLight(k.num+1, mqttc)
      triggers = [MqttTrigger(k.num+1, t, mqttc) for t in Discovery.trigger_types]

      discoverables = [light] + triggers
      for d in discoverables:
        d.publish()

      info = MqttKeyInfo(k.num + 1)
      
      pixel = self.lights.get_pixel(k.num)
      self.mqtt_keys += [LedKey(k, pixel, light, triggers)]

    self.cycle = colours.ColourCycler(1000, 12, 12)

  def loop(self):
    time.sleep(0.01)
    for (i, (r, g, b)) in enumerate(self.cycle.get_step()):
      self.mqtt_keys[i].set_color(r, g, b)
      #self.lights.set_pixel(i, r, g, b)
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
