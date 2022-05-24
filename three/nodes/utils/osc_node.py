
import math
from ..core.node import Node
from ..shadernode.shader_node_base_elements import abs, fract, round, sin, add, sub, mul
from .timer_node import TimerNode

class OscNode(Node):
    SINE = 'sine'
    SQUARE = 'square'
    TRIANGLE = 'triangle'
    SAWTOOTH = 'sawtooth'

    def __init__(self, method = SINE, timeNode = TimerNode()) -> None:
        super().__init__()

        self.method = method
        self.timeNode = timeNode

    def getNodeType( self, builder, *args ):
        return self.timeNode.getNodeType( builder )

    def generate( self, builder ):
        method = self.method
        timeNode = self.timeNode
        outputNode = None
        
        if method == OscNode.SINE:
            outputNode = add( mul( sin( mul( add( timeNode, .75 ), math.pi*2 ) ), .5 ), .5 )

        elif method == OscNode.SQUARE:
            outputNode = round( fract( timeNode ) )

        elif method == OscNode.TRIANGLE:
            outputNode = abs( sub( 1, mul( fract( add( timeNode, .5 ) ), 2 ) ) )

        elif method == OscNode.SAWTOOTH:
            outputNode = fract( timeNode )

        return outputNode.build( builder )
