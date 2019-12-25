class BitmapPart:
    def __init__(self, usage, count, size, offset):
        self.usage = usage
        self.count = count
        self.size = size
        self.offset = offset

        self._usages = [False for _ in range(count)]

    def set(self, usage):
        pass

    def clear(self, usage):
        pass

    def fill_buffer(self, buf):
        pass
