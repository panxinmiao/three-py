from three.structure import NoneAttribute

class NodeAttribute(NoneAttribute):

    isNodeAttribute = True

    def __init__(self, name, type) -> None:
        super().__init__()
        self.name = name
        self.type = type
