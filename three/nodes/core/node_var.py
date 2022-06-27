from three.structure import NoneAttribute

class NodeVar(NoneAttribute):

    isNodeVar = True

    def __init__(self, name, type) -> None:
        super().__init__()
        self.name = name
        self.type = type
