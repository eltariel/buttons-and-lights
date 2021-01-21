from typing import Dict, Any

import paho.mqtt.client as mqtt

from hass.discoverable import Discoverable, HOMEASSISTANT_DEV_INFO


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

    @property
    def discovery_topic(self) -> str:
        return self._discovery_topic(
            "device_automation", f"{self._btn_str}_{self._type}"
        )

    @property
    def discovery_payload(self) -> Dict[str, Any]:
        return {
            "automation_type": "trigger",
            "topic": self.topic,
            "payload": self.payload,
            "type": self._type,
            "subtype": self._subtype,
            "dev": HOMEASSISTANT_DEV_INFO,
        }

    def trigger(self):
        self._log.debug(f"  {self.topic} TRIGGER --> {self.payload}")
        self._client.publish(self.topic, self.payload)
