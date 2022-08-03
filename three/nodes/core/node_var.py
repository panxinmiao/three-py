from three.structure import NoneAttribute

class NodeVar(NoneAttribute):

    isNodeVar = True

    def __init__(self, name, type) -> None:
        super().__init__()
        if type is None:
            raise Exception('NodeVar type must be specified.')
        self.name = name
        self.type = type
