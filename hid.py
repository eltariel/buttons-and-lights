"""
Classes to mess with HID (USB key etc) output.
"""


class HidBitmapReport:
    """
    HID Bitmapped key report.

    TODO: This is broken for reports with bitmaps *and* full keys.
    """

    def __init__(self, gadget, report_len, ranges, report_id=None):
        """
        Set up a bitmapped key report.

        :param gadget: HidGadget this report belongs to.
        :param report_len: Total length of the report data (not including report_id)
        :param ranges: List of ranges of elements in the report: (start code, count of items, byte offset in the report)
        :param report_id: Optional report ID for HID descriptors with multiple reports defined.
        """
        self.gadget = gadget
        self.report_id = report_id
        self.chunks = [
            (start, start + count - 1, offset) for (start, count, offset) in ranges
        ]
        self.len = report_len + (0 if report_id is None else 1)
        self._buf = bytearray([0x00 for _ in range(report_len)])
        self._id_offset = 0
        if report_id is not None:
            self._buf[0] = self.report_id
            self._id_offset = 1

    def press(self, key_code):
        """
        Mark a key as pressed.

        :param key_code: Key to press. Must be within the ranges specified in the constructor.
        """
        (byte, bit) = self._key_to_index(key_code)
        self._buf[byte] |= 1 << bit

    def release(self, key_code):
        """
        Mark a key as released.

        :param key_code: Key to release. Must be within the ranges specified in the constructor.
        """
        (byte, bit) = self._key_to_index(key_code)
        self._buf[byte] &= ~(1 << bit)

    def send(self):
        """
        Send the current state of the report.
        """
        self.gadget.send_report(self._buf)

    def _key_to_index(self, key_code):
        (offset, start) = next(
            (
                (offset, start)
                for (start, end, offset) in self.chunks
                if start <= key_code < end
            ),
            (None, None),
        )
        if offset is None or start is None:
            print("Unmapped keycode {}".format(key_code))
        else:
            pos = (key_code - start) & 0x00FF
            (byte, bit) = divmod(pos, 8)
            return byte + offset + self._id_offset, bit

    def key_handler(self, key_code):
        def _handle_key_code(button, key):
            if button.is_held:
                print("Keycode {} held".format(key_code))
            elif button.is_pressed:
                print("Keycode {} pressed".format(key_code))
                self.press(key_code)
                self.send()
            else:
                print("Keycode {} released".format(key_code))
                self.release(key_code)
                self.send()

        return _handle_key_code

class BitmapPart:
    def __init__(self, usage, count, size, offset):
        self.usage = usage
        self.count = count
        self.size = size
        self.offset = offset

        self._usages = [false for _ in range(count)]

    def set(self, usage):
        pass

    def clear(self, usage):
        pass

    def fill_buffer(self, buf):
        pass

class HidGadget:
    """
    HID Gadget, for sending reports to the host.

    TODO: support input reports.
    """

    def __init__(self, dev):
        """
        Initialise the HID gadget.

        :param dev: the device path to use, e.g. /dev/hidg0
        """
        self.dev = dev

    def send_report(self, report_bytes):
        """
        Sends a report.

        This is intended to be used through a HidReport object, but can be used for arbitrary data.

        :param report_bytes: byte array to send.
        """
        with open(self.dev, "rb+") as gadget:
            print("Attempting to write a HID report: {}".format(report_bytes))
            gadget.write(report_bytes)
