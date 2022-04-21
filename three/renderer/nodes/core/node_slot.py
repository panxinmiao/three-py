from ....structure import NoneAttribute

class NodeSlot(NoneAttribute):

    def __init__(self, node, name, output) -> None:
        super().__init__()
        self.node = node
        self.name = name
        self.output = output