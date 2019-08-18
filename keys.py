from gpiozero import Button

class Key:
    def __init__(self, gpio, key_code=None, hid_report=None, handler=None):
        self.gpio = gpio
        self.handler = handler
        self.button = Button(self.gpio)
        self.button.when_pressed = self._handler
        self.button.when_released = self._handler
        self.button.when_held = self._handler
        
        self.handlers = []
        if key_code is not None and hid_report is not None:
            self.handlers.append(self._generate_key_handler(key_code, hid_report))

        if handler is not None:
            self.handlers.append(handler)

    def add_handler(self, handler):
        if handler is not None:
            self.handlers.append(handler)

    def _handler(self, button):
        if self.handler is not None:
            self.handler(button)

        for h in self.handlers:
            h(button)

    def _generate_key_handler(self, key_code, hid_report):
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
    def __init__(self, keys):
        self.keys = keys

    def add_handler(self, key, handler):
        self.keys[key].add_handler(handler)

