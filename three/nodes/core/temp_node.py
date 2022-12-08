from .node import Node
from .node_builder import NodeBuilder

class TempNode(Node):

    isTempNode = True

    def __init__(self, type = None) -> None:
        super().__init__(type)

    def hasDependencies(self, builder):
        nodeData = builder.getDataFromNode(self)
        return nodeData.dependenciesCount and nodeData.dependenciesCount > 1

    def build( self, builder:'NodeBuilder', output = None ):

        buildStage = builder.getBuildStage()

        if buildStage == 'generate':
            type = builder.getVectorType(self.getNodeType(builder, output))
            nodeData = builder.getDataFromNode(self)

            if builder.context.tmpRead != False and nodeData.propertyName:

                return builder.format(nodeData.propertyName, type, output)

            elif builder.context.tempWrite != False and type != 'void' and output != 'void' and self.hasDependencies(builder):

                snippet = super().build( builder, type )

                nodeVar = builder.getVarFromNode( self, type )
                propertyName = builder.getPropertyName( nodeVar )
                builder.addFlowCode( f'{propertyName} = {snippet}' )

                nodeData.snippet = snippet
                nodeData.propertyName = propertyName

                return builder.format( nodeData.propertyName, type, output )
        
        return super().build( builder, output )