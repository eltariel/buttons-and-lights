from gpiozero import Button

class Key:
    def __init__(self, k):
        self.k = k
        self.__dict__.update(k)
        self.button = Button(self.gpio)
        self.button.when_pressed = self._handler
        self.button.when_released = self._handler
        self.button.when_held = self._handler
        
        self.handlers = []
        try:
            if self.key_code is not None:
                self.handlers.append(self._handle_key_code)
        except AttributeError:
            self.key_code = None

        try:
            if self.handler is not None:
                self.handlers.append(self.handler)
        except AttributeError:
            self.handler = None

    def add_handler(self, handler):
        if handler is not None:
            self.handlers.append(handler)

    def _handler(self, button):
        if self.handler is not None:
            self.handler(button)

        for h in self.handlers:
            h(button)

    def _handle_key_code(self, button):
        if button.is_held:
            print("Keycode {} held".format(self.key_code))
        elif button.is_pressed:
            print("Keycode {} pressed".format(self.key_code))
            self.hid_report.press(self.key_code)
            self.hid_report.send()
        else:
            print("Keycode {} released".format(self.key_code))
            self.hid_report.release(self.key_code)
            self.hid_report.send()

            
class Keypad:
    def __init__(self, keymap):
        self.keys = [Key(k) for k in keymap]

    def add_handler(self, key, handler):
        self.keys[key].add_handler(handler)

