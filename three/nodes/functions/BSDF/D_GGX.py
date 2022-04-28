from ...shader.shader_node import ShaderNode
from ...shader.shader_node_elements import add, sub, mul, div, pow2
import math

def __D_GGX( inputs ):
    #const { alpha, dotNH } = inputs;
    alpha = inputs['alpha']
    dotNH = inputs['dotNH']
    a2 = pow2( alpha )
    
    denom = add( mul( pow2( dotNH ), sub( a2, 1.0 ) ), 1.0 ); # avoid alpha = 0 with dotNH = 1
    return mul( 1/ math.pi, div( a2, pow2( denom ) ) )
    
D_GGX = ShaderNode( __D_GGX ); # validated