from .temp_node import TempNode
from .node_builder import NodeBuilder

class FunctionCallNode(TempNode):

    isFunctionCallNode = True

    def __init__(self, functionNode = None, parameters = None) -> None:
        super().__init__()
        self.functionNode = functionNode
        self.parameters = parameters or {}

    def setParameters( self, parameters ):
        self.parameters = parameters
        return self

    def getParameters( self ):
        return self.parameters

    def getNodeType( self, builder , *args ):
        return self.functionNode.getNodeType( builder )

    def generate( self, builder:'NodeBuilder' ):

        params = []

        functionNode = self.functionNode

        inputs = functionNode.getInputs( builder )
        parameters = self.parameters

        if isinstance( parameters, list ):
            for i in range( len( parameters ) ):
                inputNode = inputs[ i ]
                node = parameters[ i ]
                params.append( node.build( builder, inputNode.type ) )
        else:

            for inputNode in inputs:
                node = parameters[ inputNode.name ]

                if node:
                    params.append( node.build( builder, inputNode.type ) )
                else:
                    raise Exception( "FunctionCallNode: Input '{inputNode.name}' not found in FunctionNode." )

        functionName = functionNode.build( builder, 'property' )

        return f"{functionName}( {', '.join(params)} )"
