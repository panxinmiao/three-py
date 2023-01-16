from ..structure import NoneAttribute

class Image(NoneAttribute):
    def __init__(self, data, width, height, depth=1) -> None:
        self.data = data
        self.width = width
        self.height = height
        self.depth = depth

