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
Currently a bit messy, you'll need to do all of this by hand.

- (optional) create `descriptor/mac-host` and `descriptor/mac-dev` containing the MAC addresses for the USB NIC.
- copy `services\*.service` to `/etc/systemd/system`
- edit both service files to point to the correct location
- enable and start the services:

      systemctl daemon-reload
      systemctl enable usb-gadget.service
      systemctl start usb-gadget.service
      systemctl enable buttons-and-lights.service
      systemctl start buttons-and-lights.service
      
- configure static USB Ethernet gadget IP
- setup dnsmasq for dhcp
- serial-getty on USB serial gadget
- systemd service for launching python script

# Key Mapping
TODO:

- currently, just mess with buttons-and-lights.py
- future: look into dynamic reloading python magic?

# LED magic

