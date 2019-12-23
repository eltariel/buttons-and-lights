"""
Library for using GPIO pins as buttons.
"""

from gpiozero import Button


class Key:
    """
    GPIO pin handler, with HID keycode sending and arbitrary handler methods.
    """

    def __init__(self, num, gpio, key_code=None, hid_report=None, handler=None):
        """
        Set up the key.

        :param gpio: GPIO pin to bind to.
        :param key_code: Optional key code to send when the key is pressed. Needs hid_report defined too.
        :param hid_report: HID report to send key_code
        :param handler: Optional handler method.
        """
        self.gpio = gpio
        self.handler = handler
        self.num = num
        self.button = Button(self.gpio)
        self.button.when_pressed = self._handler
        self.button.when_released = self._handler
        self.button.when_held = self._handler

        self.keycode = key_code
        self.hid_report = hid_report

        if key_code is not None and hid_report is not None:
            self.handler = self._generate_key_handler(key_code, hid_report)

    def add_handler(self, handler):
        """
        Adds a handler to the key.

        If a handler already exists, this handler will *replace* the existing one.

        :param handler: handler function to call. Should take a single argument which is passed the GPIO button.
        """
        if handler is not None:
            self.handler = handler

    def _handler(self, button):
        if self.handler is not None:
            self.handler(button, self)


class Keypad:
    """
    A collection of keys.

    TODO: Make this more useful.
    """

    def __init__(self, keys):
        """
        Create this.

        :param keys: A list of Keys.
        """
        self._in_layer_select = False
        self.current_layer = 0
        self.keys = keys
        self.layers = [[]]

        self.keys[0].add_handler(self._layer_button_handler)
        for i in range(1,12):
            self.keys[i].add_handler(self._key_handler)

    def add_handler(self, key, layer, handler):
        """
        Add a handler to the key at a given index.

        :param key: Key index.
        :param handler: handler to add.
        """
        self.keys[key].add_handler(handler)

    def add_layers(self, layers):
        self.layers = layers

    def select_layer(self, layer_index):
        self.current_layer = self.layers[layer_index]

    def _button_handler(self, button, key):
        self.current_layer.handler[(row, column)](button, key)

    def _layer_button_handler(self, button, key):
        if button.is_held:
            pass
        elif button.is_pressed:
            self._in_layer_select = True
            print("entering layer select mode")
        else:
            self._in_layer_select = False
            print("exiting layer select mode, layer is now {}".format(self.current_layer))

    def _key_handler(self, button, key):
        if self._in_layer_select:
            if button.is_held:
                pass
            elif button.is_pressed:
                self.current_layer = key.num - 1

        else:
            self.layers[self.current_layer][key.num - 1](button, key)

