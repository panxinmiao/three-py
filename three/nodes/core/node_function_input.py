from three.structure import NoneAttribute

class NodeFunctionInput(NoneAttribute):

    def __init__(self, type, name, count = None, qualifier = '', isConst = False) -> None:
        super().__init__()
        self.type = type
        self.name = name
        self.count = count
        self.qualifier = qualifier
        self.isConst = isConst