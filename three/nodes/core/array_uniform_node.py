from .uniform_node import UniformNode 

class ArrayUniformNode(UniformNode):

    isArrayUniformNode = True

    def __init__(self, nodes = None) -> None:
        super().__init__()
        self.nodes = nodes or []

    def getNodeType(self, builder, *args ):
        return self.nodes[ 0 ].getNodeType( builder )