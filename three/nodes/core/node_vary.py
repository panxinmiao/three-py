from three.structure import NoneAttribute

class NodeVary(NoneAttribute):
    
    isNodeVary = True

    def __init__(self, name, type) -> None:
        super().__init__()
        self.name = name
        self.type = type
