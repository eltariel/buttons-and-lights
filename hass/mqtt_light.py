import json
from dataclasses import dataclass, asdict

from hass.discoverable import Discoverable, HOMEASSISTANT_DEV_INFO
from njak import HOST_NAME, mc


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
    if self._state != value:
      self._state = value
      for l in self._listeners:
        l(self)

  def set(self, on: bool, brightness: int, color: RGBColor):
    self.state = LightState(on, brightness, color)

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
    self._client.publish(self.state_topic, self._state.to_payload())

  def add_listener(self, listener):
    self._log.debug(f"Adding listener: {listener}")
    self._listeners += [listener]

  def listen(self):
    self._log.debug(f"Listening on {self.listen_topic}")
    self._client.message_callback_add(self.listen_topic, self._handle_message)

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
