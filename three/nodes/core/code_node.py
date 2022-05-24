#from three.renderer.nodes import Node, NodeBuilder

from .node import Node
from .node_builder import NodeBuilder

class CodeNode(Node):

    def __init__(self, code='', nodeType='code') -> None:
        super().__init__(nodeType=nodeType)
        self.code = code
        self._includes = []

    def setIncludes( self, includes ):
        self._includes = includes
        return self

    def getIncludes(self, *args):
        '''/*builder*/ '''
        return self._includes


    def generate(self, builder:'NodeBuilder' ):
        
        includes = self.getIncludes( builder )

        for include in includes:
            include.build( builder )

        nodeCode = builder.getCodeFromNode( self, self.getNodeType( builder ) )
        nodeCode.code = self.code

        return nodeCode.code
    