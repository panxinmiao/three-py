from ..core.temp_node import TempNode
from ..shadernode.shader_node_base_elements import EPSILON, vec3, sub, mul, div, cond, lessThan, equal, max
from ..shadernode.shader_node import ShaderNode

def __burn( base, blend ):
    def fn(c):
        return cond( lessThan( blend[ c ], EPSILON ), blend[ c ], max( sub( 1.0, div( sub( 1.0, base[ c ] ), blend[ c ] ) ), 0 ) )
    
    return vec3( fn( 'x' ), fn( 'y' ), fn( 'z' ) )

BurnNode = ShaderNode(__burn)

def __dodge( base, blend ):
    def fn(c):
        return cond( equal( blend[ c ], 1.0 ), blend[ c ], max( div( base[ c ], sub( 1.0, blend[ c ] ) ), 0 ) )
    
    return vec3( fn( 'x' ), fn( 'y' ), fn( 'z' ) )

DodgeNode = ShaderNode(__dodge)

def __screen( base, blend ):
    def fn(c):
        return sub( 1.0, mul( sub( 1.0, base[ c ] ), sub( 1.0, blend[ c ] ) ) )
    
    return vec3( fn( 'x' ), fn( 'y' ), fn( 'z' ) )

ScreenNode = ShaderNode(__screen)

def __overlay( base, blend ):
    def fn(c):
        return cond( lessThan( base[ c ], 0.5 ), mul( 2.0, base[ c ], blend[ c ] ), sub( 1.0, mul( sub( 1.0, base[ c ] ), sub( 1.0, blend[ c ] ) ) ) )
    
    return vec3( fn( 'x' ), fn( 'y' ), fn( 'z' ) )

OverlayNode = ShaderNode(__overlay)


class BlendModeNode(TempNode):

    BURN = 'burn'
    DODGE = 'dodge'
    SCREEN = 'screen'
    OVERLAY = 'overlay'

    def __init__(self, blendMode, baseNode, blendNode) -> None:
        super().__init__()

        self.blendMode = blendMode
        self.baseNode = baseNode
        self.blendNode = blendNode
    
    def construct( self, *args ):

        blendMode = self.blendMode
        baseNode = self.baseNode
        blendNode = self.blendNode

        # params = { 'base': baseNode, 'blend': blendNode }

        outputNode = None

        if blendMode == BlendModeNode.BURN:
            outputNode = BurnNode(baseNode, blendNode)
        elif blendMode == BlendModeNode.DODGE:
            outputNode = DodgeNode(baseNode, blendNode)
        elif blendMode == BlendModeNode.SCREEN:
            outputNode = ScreenNode(baseNode, blendNode)
        elif blendMode == BlendModeNode.OVERLAY:
            outputNode = OverlayNode(baseNode, blendNode)
        
        return outputNode