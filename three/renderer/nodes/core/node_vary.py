from ....structure import NoneAttribute

class NodeVary(NoneAttribute):

    def __init__(self, name, type) -> None:
        super().__init__()
        self.name = name
        self.type = type
