# Buttons and Lights
Python interface for GPIO keypads and APA102 RGB LEDs. Inspired by the Pimoroni Keybow.

# Requirements
- Python 3
- SpiDev
- gpiozero

# Setup
## One-off
As root:

    ./init-usb-gadget.sh
    python3 buttons-and-lights.py


## Installation
TODO:

- systemd service for starting gadget
- configure static USB Ethernet gadget IP
- setup dnsmasq for dhcp
- serial-getty on USB serial gadget
- systemd service for launching python script

# Key Mapping
TODO:

- currently, just mess with buttons-and-lights.py
- future: look into dynamic reloading python magic?

# LED magic

