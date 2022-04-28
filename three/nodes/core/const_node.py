from .input_node import InputNode

class ConstNode(InputNode):

    def generateConst( self, builder ):
        return builder.getConst( self.getNodeType( builder ), self.value )


    def generate(self, builder, output ):
        type = self.getNodeType( builder )
        return builder.format( self.generateConst( builder ), type, output )