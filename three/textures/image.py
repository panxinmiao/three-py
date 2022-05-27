from ..structure import NoneAttribute

class Image(NoneAttribute):
    def __init__(self, data, width, height) -> None:
        self.data = data
        self.width = width
        self.height = height

