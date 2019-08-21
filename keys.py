"""
Library for using GPIO pins as buttons.
"""

from gpiozero import Button


class Key:
    """
    GPIO pin handler, with HID keycode sending and arbitrary handler methods.
    """
    def __init__(self, gpio, key_code=None, hid_report=None, handler=None):
        """
        Set up the key.

        :param gpio: GPIO pin to bind to.
        :param key_code: Optional key code to send when the key is pressed. Needs hid_report defined too.
        :param hid_report: HID report to send key_code
        :param handler: Optional handler method.
        """
        self.gpio = gpio
        self.handler = handler
        self.button = Button(self.gpio)
        self.button.when_pressed = self._handler
        self.button.when_released = self._handler
        self.button.when_held = self._handler
        
        self.handlers = []
        if key_code is not None and hid_report is not None:
            self.handlers.append(self._generate_key_handler(key_code, hid_report))

    def add_handler(self, handler):
        """
        Adds a handler to the key.

        If a handler already exists, this handler will be called *after* the existing one.

        :param handler: handler function to call. Should take a single argument which is passed the GPIO button.
        """
        if handler is not None:
            self.handlers.append(handler)

    def _handler(self, button):
        if self.handler is not None:
            self.handler(button)

        for h in self.handlers:
            h(button)

    @staticmethod
    def _generate_key_handler(key_code, hid_report):
        def _handle_key_code(button):
            if button.is_held:
                print("Keycode {} held".format(key_code))
            elif button.is_pressed:
                print("Keycode {} pressed".format(key_code))
                hid_report.press(key_code)
                hid_report.send()
            else:
                print("Keycode {} released".format(key_code))
                hid_report.release(key_code)
                hid_report.send()
        return _handle_key_code


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
        self.keys = keys

    def add_handler(self, key, handler):
        """
        Add a handler to the key at a given index.

        :param key: Key index.
        :param handler: handler to add.
        """
        self.keys[key].add_handler(handler)
