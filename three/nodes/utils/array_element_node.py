from ..core.node import Node

class ArrayElementNode(Node):

    def __init__(self, node, indexNode ) -> None:
        super().__init__()
        self.node = node
        self.indexNode = indexNode

    def getNodeType( self, builder, *args ):
        return self.node.getNodeType( builder )

    def generate( self, builder ):
        nodeSnippet = self.node.build( builder )
        indexSnippet = self.indexNode.build( builder, 'uint' )
        return f'{nodeSnippet}[ {indexSnippet} ]'
