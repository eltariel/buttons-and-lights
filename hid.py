class HidBitmapReport:
    def __init__(self, gadget, reportlen, report_id=None):
        self.gadget = gadget
        self.len = reportlen + (0 if report_id is None else 1)
        self.report_id = report_id
        self._buf = bytearray([0x00 for _ in range(reportlen)])

    def press(self, key_code):
        (byte, bit) = self._key_to_index(key_code)
        print("buf[{}] = {}, 1 << {} = {}".format(byte, self._buf[byte], bit, 1 << bit))
        self._buf[byte] |= 1 << bit
        print("buf[{}] | (1 << {}) = {}".format(byte, bit, self._buf[byte]))
        print("Buffer is now {}".format(self._buf))


    def release(self, key_code):
        (byte, bit) = self._key_to_index(key_code)
        self._buf[byte] &= ~(1 << bit)

    def send(self):
        self.gadget.send_report(self._get())

    def _get(self):
        if self.report_id is not None:
            return bytearray([self.report_id, *self._buf])
        else:
            return bytearray(self._buf)

    def _key_to_index(self, key_code):
        pos = key_code & 0x00FF
        bb = divmod(pos, 8)
        print(bb)
        (byte, bit) = bb
        return (byte + 1, bit) # First byte is mods

class HidGadget:
    def __init__(self, dev):
        self.dev = dev

    def send_report(self, report_bytes):
        with open(self.dev, 'rb+') as hidg:
            print("Attempting to write a HID report: {}".format(report_bytes))
            hidg.write(report_bytes)

