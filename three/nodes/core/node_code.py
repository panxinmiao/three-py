from three.structure import NoneAttribute

class NodeCode(NoneAttribute):

    def __init__(self, name, type, code = '') -> None:
        super().__init__()
        self.name = name
        self.type = type
        self.code = code
