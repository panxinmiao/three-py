from .node import Node
from ..math.operator_node import OperatorNode

class StackNode(Node):

    isStackNode = True

    def __init__(self) -> None:
        super().__init__()
        
        self.nodes = []
        self.outputNode = None

    def getNodeType(self, builder):
        return self.outputNode.getNodeType(builder) if self.outputNode else 'void'
    
    def assign(self, targetNode, sourceValue):
        self.nodes.append(OperatorNode('=', targetNode, sourceValue))
        return self

    def build(self, builder, *args):
        for node in self.nodes:
            node.build(builder)
        
        if self.outputNode:
            return self.outputNode.build(builder, *args)
        else:
            return super().build(builder, *args)