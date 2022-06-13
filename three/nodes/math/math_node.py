# from three.renderer.nodes import TempNode, ExpressionNode, SplitNode, OperatorNode

from ..core.temp_node import TempNode
from ..core.expression_node import ExpressionNode
from ..utils.split_node import SplitNode
from ..utils.join_node import JoinNode
from .operator_node import OperatorNode

class MathNode(TempNode):
    # 1 input

    RADIANS = 'radians'
    DEGREES = 'degrees'
    EXP = 'exp'
    EXP2 = 'exp2'
    LOG = 'log'
    LOG2 = 'log2'
    SQRT = 'sqrt'
    INVERSE_SQRT = 'inversesqrt'
    FLOOR = 'floor'
    CEIL = 'ceil'
    NORMALIZE = 'normalize'
    FRACT = 'fract'
    SIN = 'sin'
    COS = 'cos'
    TAN = 'tan'
    ASIN = 'asin'
    ACOS = 'acos'
    ATAN = 'atan'
    ABS = 'abs'
    SIGN = 'sign'
    LENGTH = 'length'
    NEGATE = 'negate'
    INVERT = 'invert'
    DFDX = 'dFdx'
    DFDY = 'dFdy'
    SATURATE = 'saturate'
    ROUND = 'round'

    # 2 inputs
    
    ATAN2 = 'atan2'
    MIN = 'min'
    MAX = 'max'
    MOD = 'mod'
    STEP = 'step'
    REFLECT = 'reflect'
    DISTANCE = 'distance'
    DOT = 'dot'
    CROSS = 'cross'
    POW = 'pow'
    TRANSFORM_DIRECTION = 'transformDirection'

    # 3 inputs

    MIX = 'mix'
    CLAMP = 'clamp'
    REFRACT = 'refract'
    SMOOTHSTEP = 'smoothstep'
    FACEFORWARD = 'faceforward'


    def __init__(self, method, aNode, bNode = None, cNode = None) -> None:
        super().__init__()

        self.method = method

        self.aNode = aNode
        self.bNode = bNode
        self.cNode = cNode

    def getInputType( self, builder, *args ):

        aType = self.aNode.getNodeType( builder )
        bType = self.bNode.getNodeType( builder ) if self.bNode else None
        cType = self.cNode.getNodeType( builder ) if self.cNode else None

        aLen = 0 if aType and builder.isMatrix( aType ) else builder.getTypeLength( aType )
        bLen = 0 if bType and builder.isMatrix( bType ) else builder.getTypeLength( bType )
        cLen = 0 if cType and builder.isMatrix( cType ) else builder.getTypeLength( cType )

        if aLen > bLen and aLen > cLen :
            return aType

        elif bLen > cLen :
            return bType

        elif cLen > aLen :
            return cType

        return aType



    def getNodeType( self, builder, *args ):

        method = self.method

        if method == MathNode.LENGTH or method == MathNode.DISTANCE or method == MathNode.DOT:
            return 'float'

        elif method == MathNode.CROSS:
            return 'vec3'

        else:
            return self.getInputType( builder )


    def generate( self, builder, output, *args ):
        method = self.method
        type = self.getNodeType( builder )
        inputType = self.getInputType( builder )

        a = self.aNode
        b = self.bNode
        c = self.cNode

        isWebGL = builder.renderer.isWebGLRenderer == True

        if isWebGL and ( method == MathNode.DFDX or method == MathNode.DFDY ) and output == 'vec3':
            return JoinNode( [
                MathNode( method, SplitNode( a, 'x' ) ),
                MathNode( method, SplitNode( a, 'y' ) ),
                MathNode( method, SplitNode( a, 'z' ) )
            ] ).build( builder )

        if method == MathNode.TRANSFORM_DIRECTION:

            # dir can be either a direction vector or a normal vector
            # upper-left 3x3 of matrix is assumed to be orthogonal

            tA = a
            tB = b

            if builder.isMatrix( tA.getNodeType( builder ) ):

                tB = ExpressionNode( f"{ builder.getType( 'vec4' ) }( { tB.build( builder, 'vec3' ) }, 0.0 )", 'vec4' )

            else:

                tA = ExpressionNode( f"{ builder.getType( 'vec4' ) }( { tA.build( builder, 'vec3' ) }, 0.0 )", 'vec4' )


            mulNode = SplitNode( OperatorNode( '*', tA, tB ), 'xyz' )

            return MathNode( MathNode.NORMALIZE, mulNode ).build( builder )


        if method == MathNode.SATURATE:
            # return f'clamp( { a.build( builder, inputType ) }, 0.0, 1.0 )'
            return builder.format( f'clamp( { a.build( builder, inputType ) }, 0.0, 1.0 )', type, output )

        if method == MathNode.NEGATE:
            # return '( -' + a.build( builder, inputType ) + ' )'
            return builder.format( '( -' + a.build( builder, inputType ) + ' )', type, output )

        elif method == MathNode.INVERT:
            # return '( 1.0 - ' + a.build( builder, inputType ) + ' )'
            return builder.format( '( 1.0 - ' + a.build( builder, inputType ) + ' )', type, output )

        else:
            params = []

            if method == MathNode.CROSS:
                params.extend([
                    a.build( builder, type ),
                    b.build( builder, type )
                ])

            elif method == MathNode.STEP:
                params.extend([
                    a.build( builder, 'float' if builder.getTypeLength( a.getNodeType( builder ) ) == 1 else inputType ), 
                    b.build( builder, inputType )
                ])

            elif (isWebGL and (method == MathNode.MIN or method == MathNode.MAX)) or method == MathNode.MOD:
                params.extend([
                    a.build( builder, inputType ),
                    b.build( builder, 'float' if builder.getTypeLength( b.getNodeType( builder ) ) == 1 else inputType )
                ])

            elif method == MathNode.REFRACT:
                params.extend([
                    a.build( builder, inputType ),
                    b.build( builder, inputType ),
                    c.build( builder, 'float' )
                ])

            elif method == MathNode.MIX:
                params.extend([
                    a.build( builder, inputType ),
                    b.build( builder, inputType ),
                    c.build( builder, 'float' if builder.getTypeLength( c.getNodeType( builder ) ) == 1 else inputType )
                ])

            else:
                params.append( a.build( builder, inputType ) )

                if c:
                    params.append( b.build( builder, inputType ))
                    params.append( c.build( builder, inputType ))

                elif b:
                    params.append( b.build( builder, inputType ))


            # return f"{method}( {', '.join(params)} )"

            return builder.format( f"{ builder.getMethod( method ) }( {', '.join(params)} )", type, output )
