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
## Layout
The physical mapping is defined in the `layout` array in config.py. This is an array of 12 tuples of (led index, key gpio)
and they're configured by default to match the Keybow (because that's what I'm working with).

    9(0, 20)   A(4, 16)   B(8, 26)
    6(1, 6)    7(5, 12)   8(9, 13)
    3(2, 22)   4(6, 24)   5(A, 5)
    0(3, 17)   1(7, 27)   2(B, 23)


## Key handlers
The key mappings and other behaviours are specified in the constructor of the `Njak` class. This creates a number of handlers
that get bound to the GPIO keys. The handlers must accept two arguments: the gpiozero Button instance and the njak Key object.

The Bitmap HID report contains a helper to generate handlers for key presses. 


## Layers
Key handlers are grouped into layers. Key 0 (bottom left on the Keybow) is reserved to switch between layers. Currently,
layers are defined in a 2D array in the `Njak` constructor and passed into the `Keypad` class. It's a little broken but
I'm working on it...

Switch between layers by holding key 0 and then pressing the key corresponding to the desired layer. The key
representing the selected layer will go dark.

Default layers:
0: Keys 0 - 9 and enter
1: Every key is F13. I use it for Discord PTT :P


## Future:
- Work out some new things to do with it :P
- Auto-type strings
- Multi-key sequences

# LED magic
TODO
