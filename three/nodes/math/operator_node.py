# from three.renderer.nodes import TempNode
from ..core.temp_node import TempNode
import three

class OperatorNode(TempNode):

    def __init__(self, op, aNode, bNode, *params) -> None:
        super().__init__()

        self.op = op

        if len(params) > 0:
            finalBNode = bNode
            for p in params:
                finalBNode =  OperatorNode( op, finalBNode, p )

            bNode = finalBNode

        self.aNode = aNode
        self.bNode = bNode

    def hasDependencies(self, builder):
        return super().hasDependencies(builder) if self.op != '=' else False

    def getNodeType( self, builder:'three.NodeBuilder', output = None ):

        op = self.op
        typeA = self.aNode.getNodeType( builder )
        typeB = self.bNode.getNodeType( builder )


        if typeA == 'void' or typeB == 'void':
            return 'void'
        elif op == '=' or op == '%':
            return typeA
        elif op == '&' or op == '|' or op == '^' or op == '>>' or op == '<<':
            return builder.getIntegerType( typeA )
        elif op == '==' or op == '&&' or op == '||' or op == '^^' :
            return 'bool'
        elif op == '<=' or op == '>=' or op =='<' or op == '>':
            length = builder.getTypeLength( output )
            return f'bvec{ length }' if length > 1 else 'bool'
        else:
            if typeA == 'float' and builder.isMatrix( typeB ):
                return typeB
    
            elif builder.isMatrix( typeA ) and builder.isVector( typeB ):
                # matrix x vector
                return builder.getVectorFromMatrix( typeA )

            elif builder.isVector( typeA ) and builder.isMatrix( typeB ):

                # vector x matrix
                return builder.getVectorFromMatrix( typeB )

            elif builder.getTypeLength( typeB ) > builder.getTypeLength( typeA ):

                # anytype x anytype: use the greater length vector
                return typeB

            return typeA


    def generate( self, builder:'three.NodeBuilder', output ):

        op = self.op
        type = self.getNodeType( builder, output )

        typeA = None
        typeB = None

        if type != 'void':
            typeA = self.aNode.getNodeType( builder )
            typeB = self.bNode.getNodeType( builder )
            if op == '=':
                typeB = typeA
            elif op == '<=' or op == '>=' or op =='<' or op == '>':
                if builder.isVector( typeA ):
                    typeB = typeA
                else:
                    typeA = typeB = 'float'

            elif op == '>>' or op == '<<':
                typeA = type
                typeB = builder.changeComponentType( typeB, 'uint' )

            elif builder.isMatrix( typeA ) and builder.isVector( typeB ):
                # matrix x vector
                typeB = builder.getVectorFromMatrix( typeA )

            elif builder.isVector( typeA ) and builder.isMatrix( typeB ):
                # vector x matrix
                typeA = builder.getVectorFromMatrix( typeB )

            else:
                # anytype x anytype
                typeA = typeB = type
        else:
            typeA = typeB = type

        a = self.aNode.build( builder, typeA )
        b = self.bNode.build( builder, typeB )
        outputLength = builder.getTypeLength( output )

        if output != 'void':
            if op == '=':
                builder.addFlowCode( f"{a} {self.op} {b}" )

                return a

            elif op == '<' and outputLength > 1:
                return builder.format( f"{ builder.getMethod( 'lessThan' ) }( {a}, {b} )", type, output )

            elif op == '<=' and outputLength > 1:
                return builder.format( f"{ builder.getMethod( 'lessThanEqual' ) }( {a}, {b} )", type, output )

            elif op == '>' and outputLength > 1:
                return builder.format( f"{ builder.getMethod( 'greaterThan' ) }( {a}, {b} )", type, output )

            elif op == '>=' and outputLength > 1:
                return builder.format( f"{ builder.getMethod( 'greaterThanEqual' ) }( {a}, {b} )", type, output )

            else:
                #return f"( {a} {self.op} {b} )"
                return builder.format( f"( {a} {self.op} {b} )", type, output )


        elif typeA != 'void':
            # return f"{a} {self.op} {b}"
            return builder.format( f"{a} {self.op} {b}", type, output )



