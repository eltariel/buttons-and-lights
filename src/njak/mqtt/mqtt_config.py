import json
from dataclasses import dataclass
from pathlib import Path

from util.dataclass_json_encoder import DataclassJSONEncoder

with open("/sys/class/net/wlan0/address") as f:
  MAC_ADDR = f.read().strip().replace(":", "")


DEFAULT_CLIENTID = f"njak_{MAC_ADDR}"


@dataclass
class MqttLWT:
  topic: str = f"{DEFAULT_CLIENTID}/status"
  alive: str = "online"
  dead: str = "offline"


@dataclass
class MqttConfig:
  host: str
  port: int
  user: str = None
  password: str = None

  client_id: str = DEFAULT_CLIENTID

  lwt: MqttLWT = MqttLWT()

  device_root: str = "njak"
  discovery_root: str = "homeassistant"

  def write(self, cfg_file: Path):
    with open(cfg_file, "w") as f:
      json.dump(self, f, cls=DataclassJSONEncoder, indent=2)

  @staticmethod
  def read(cfg_file: Path):
    try:
      with open(cfg_file, "r") as f:
        c = json.load(f)
        print(c)
        l = c.get("lwt")
        lwt = MqttLWT(l.get("topic"),
                      l.get("alive"),
                      l.get("dead")) if l else None
        cfg = MqttConfig(c["host"],
                         c["port"],
                         c.get("user"),
                         c.get("password"),
                         c.get("client_id"),
                         lwt,
                         c.get("device_root"),
                         c.get("discovery_root"))
    except Exception as e:
      print(f"Load failed, getting default instead ({e!r})")
      cfg = MqttConfig.default()
    return cfg

  @staticmethod
  def default():
    return MqttConfig("localhost", 1883)
