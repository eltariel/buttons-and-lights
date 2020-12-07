import json
import logging

import paho.mqtt.client as mqtt
from mqtt.mqtt_config import MAC_ADDR
from njak import mc, HOST_NAME


class Discoverable:
  DEVICE_ROOT = f"njak"
  DISCOVERY_ROOT = f"homeassistant"

  def __init__(self, mqtt_client: mqtt.Client):
    self._client = mqtt_client
    self._log = logging.getLogger(type(self).__name__)

  def publish(self):
    #self._log.debug(f"  PUBLISH {self.discovery_topic} --> {json.dumps(self.discovery_payload, indent=2)}")
    self._client.publish(self.discovery_topic, json.dumps(self.discovery_payload), retain=True)

  def unpublish(self):
    #self._log.debug(f"  UNPUBLISH {self.discovery_topic}")
    self._client.publish(self.discovery_topic, None)

  def _topic(self, component_id: str) -> str:
    return f"{self.DEVICE_ROOT}/{MAC_ADDR}/{component_id}"

  def _discovery_topic(self, component_id: str, object_id: str) -> str:
    return f"{self.DISCOVERY_ROOT}/{component_id}/{mc.client_id}/{object_id}/config"


HOMEASSISTANT_DEV_INFO = {
    "cns": [("mac", MAC_ADDR)],
    "ids": [MAC_ADDR],
    "mf": "Eltariel",
    "mdl": "Pimoroni Keybow + NJAK",
    "sw": "TBA",
    "name": f"Keybow {HOST_NAME}"
    }
