#from three.renderer.nodes import InputNode
from .uniform_node import UniformNode 

class ArrayUniformNode(UniformNode):

    def __init__(self, nodes = None) -> None:
        super().__init__()
        self.nodes = nodes or []

    def getNodeType(self, builder):
        return self.nodes[ 0 ].getNodeType( builder )