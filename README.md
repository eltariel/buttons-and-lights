# Not Just A Keypad
Python interface for GPIO keypads and APA102 RGB LEDs. Inspired by the Pimoroni Keybow.

# Requirements
- Python 3
- SpiDev
- gpiozero

# Setup
## One-off
As root:

    ./init-usb-gadget.sh
    python3 njak.py


## Installation
Currently a bit messy, you'll need to do all of this by hand.

- (optional) create `descriptor/mac-host` and `descriptor/mac-dev` containing the MAC addresses for the USB NIC.
- copy `services\*.service` to `/etc/systemd/system`
- edit both service files to point to the correct location
- enable and start the services:

      systemctl daemon-reload
      systemctl enable njak-usb-gadget.service
      systemctl start njak-usb-gadget.service
      systemctl enable njak.service
      systemctl start njak.service
      
- configure static USB Ethernet gadget IP
- setup dnsmasq for dhcp
- serial-getty on USB serial gadget
- systemd service for launching python script

# Key Mapping
## Default keys
The initial mapping assumes 12 keys in a 4x3 grid:

    k   -   m
    g   h   i
    d   e   f
    !   b   c

All of the keys send the appropriate HID code for that letter, except for '-' (top middle) which does nothing, and
'!' (bottom left) which reloads the behaviours module.

## Editing behaviours
The key mappings and other behaviours are specified in behaviours.py. This is a regular python module, with a few notable things:

- `behaviours.scancodes` is (currently) used to define the key mapping at initial startup. This is a
  list of integers, where each entry is the HID usage to send for the key at that index. If it's `None` then
  no keypress event occurs.
- `behaviours.init(key_pad, led_pad)` is called once after each time the behaviours are reloaded.
- `behaviours.loop(key_pad, led_pad)` is called in an infinite loop after init completes.

This will likely change again at some point.


# LED magic
TODO

