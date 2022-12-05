from ..core.node import Node

class ConvertNode(Node):
    def __init__(self, node, convertTo ) -> None:
        super().__init__()
        self.node = node
        self.convertTo:str = convertTo

    def getNodeType( self, builder ):
        requestType = self.node.getNodeType(builder)

        convertTo = None
        for overloadingType in self.convertTo.split( '|' ):
            if convertTo == None or builder.getTypeLength( requestType ) == builder.getTypeLength( overloadingType ):
                convertTo = overloadingType

        return convertTo

    def generate( self, builder, output ):
        node = self.node
        type = self.getNodeType(builder)
        snippet = node.build( builder, type )

        return builder.format( snippet, type, output )

