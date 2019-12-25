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
