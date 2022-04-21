from ....structure import NoneAttribute

class NodeUniform(NoneAttribute):

    def __init__(self, name, type, node, needsUpdate = None) -> None:
        super().__init__()
        self.name = name
        self.type = type
        self.node = node
        self.needsUpdate = needsUpdate

    @property
    def value(self):
        return self.node.value

    @value.setter
    def value(self, val):
        self.node.value = val
