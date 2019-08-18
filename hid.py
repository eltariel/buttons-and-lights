class HidBitmapReport:
    def __init__(self, gadget, reportlen, ranges, report_id=None):
        self.gadget = gadget
        self.chunks = [(start, start + count - 1, offset) for (start, count, offset) in ranges]
        self.len = reportlen + (0 if report_id is None else 1)
        self._buf = bytearray([0x00 for _ in range(reportlen)])
        self._id_offset = 0
        if report_id is not None:
            self._buf[0] = self.report_id
            self._id_offset = 1

    def press(self, key_code):
        (byte, bit) = self._key_to_index(key_code)
        self._buf[byte] |= 1 << bit

    def release(self, key_code):
        (byte, bit) = self._key_to_index(key_code)
        self._buf[byte] &= ~(1 << bit)

    def send(self):
        self.gadget.send_report(self._buf)

    def _key_to_index(self, key_code):
        (offset, start) = next(((offset, start) for (start, end, offset) in self.chunks if key_code >= start and key_code < end), (None, None))
        if offset is None or start is None:
            print("Unmapped keycode {}".format(key_code))
        else:
            pos = (key_code - start) & 0x00FF
            (byte, bit) = divmod(pos, 8)
            return (byte + offset + self._id_offset, bit)

class HidGadget:
    def __init__(self, dev):
        self.dev = dev

    def send_report(self, report_bytes):
        with open(self.dev, 'rb+') as hidg:
            print("Attempting to write a HID report: {}".format(report_bytes))
            hidg.write(report_bytes)

