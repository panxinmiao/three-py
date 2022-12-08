#from three.renderer.nodes import Node, NodeBuilder

from .node import Node
from .node_builder import NodeBuilder

class CodeNode(Node):

    isCodeNode = True

    def __init__(self, code='', includes = None) -> None:
        super().__init__('code')
        self.code = code
        self._includes = includes or []

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
    