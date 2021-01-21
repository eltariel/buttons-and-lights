import math
import json
from dataclasses import dataclass, asdict, astuple

from hass.discoverable import Discoverable, HOMEASSISTANT_DEV_INFO
from config import HOST_NAME, mc


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
        "state": "ON" if self.on else "OFF",
      })


class MqttLight(Discoverable):
  def __init__(self, button, light, mqtt_client):
    super().__init__(mqtt_client)
    self._button = button
    self._light = light
    self._btn_str = f"{button:02}"
    self._light_topic = self._topic(f"light/{self._btn_str}")
    self._state = LightState(False, 0, RGBColor(0, 0, 0))
    self._subscribed = False

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
    if self._state != value:
      self._state = value
      self._update_light()
      # self.publish_state()

  def set_color(self, r, g, b):
    self.state = LightState(self.state.on, self.state.brightness, RGBColor(r, g, b))

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
      "avty_t": mc.lwt.topic,
      "pl_avail": mc.lwt.alive,
      "pl_not_avail": mc.lwt.dead,
      "schema": "json",
      "brightness": True,
      "hs": True,
      "rgb": True,
      "dev": HOMEASSISTANT_DEV_INFO
      }

  def publish_state(self):
    p = self.state.to_payload()
    self._log.debug(f"  {self.state_topic} STATE --> {p}")
    self._client.publish(self.state_topic, self.state.to_payload())

  def listen(self):
    self._log.debug(f"Listening on {self.listen_topic}")
    self._client.message_callback_add(self.listen_topic, self._handle_message)
    if not self._subscribed:
        self._client.subscribe(self.listen_topic)
        self._subscribed = True

  def _handle_message(self, client, userdata, message):
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

    br = p.get("brightness", self.state.brightness)

    st = p.get("state")
    on = st == "ON" if st is not None else self.state.on

    curr_color = self.state.color
    c = p.get("color")
    if c is not None:
      r = c.get("r", curr_color.r)
      g = c.get("g", curr_color.g)
      b = c.get("b", curr_color.b)
      color = RGBColor(r, g, b)
    else:
      color = curr_color

    self.state = LightState(on, br, color)

  def _update_light(self):
    # TODO: move this calculation into the pixel class
    br = min(31, math.ceil(self.state.brightness / 8))
    r, g, b = astuple(self.state.color)

    if self.state.on:
      self._light.set(r, g, b, br)
    else:
      self._light.turn_off()
