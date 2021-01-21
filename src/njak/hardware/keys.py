"""
Library for using GPIO pins as buttons.
"""

from gpiozero import Button


class Key:
    """
    GPIO pin handler, with HID keycode sending and arbitrary handler methods.
    """

    def __init__(self, num, gpio, handler=None):
        """
        Set up the key.

        :param gpio: GPIO pin to bind to.
        :param handler: Optional handler method.
        """
        self.gpio = gpio
        self.handler = handler
        self.num = num
        self.button = Button(self.gpio)
        self.button.when_pressed = self._handler
        self.button.when_released = self._handler
        self.button.when_held = self._handler

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
        self.current_layer = 1
        self.keys = keys
        self.layers = {}

        self.keys[0].add_handler(self._layer_button_handler)
        for i in range(1, 12):
            self.keys[i].add_handler(self._key_handler)

    def add_layer(self, layer, handlers):
        self.layers[layer] = handlers

    def select_layer(self, layer_index):
        self.current_layer = self.layers[layer_index]

    def _layer_button_handler(self, button, key):
        if button.is_held:
            pass
        elif button.is_pressed:
            self._in_layer_select = True
            print("entering layer select mode")
        else:
            self._in_layer_select = False
            print(
                "exiting layer select mode, layer is now {}".format(self.current_layer)
            )

    def _key_handler(self, button, key):
        if self._in_layer_select:
            if button.is_held:
                pass
            elif button.is_pressed:
                if key.num in self.layers:
                    self.current_layer = key.num
        else:
            self.layers[self.current_layer][key.num - 1](button, key)
