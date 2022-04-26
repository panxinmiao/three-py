from ...shader.shader_node import ShaderNode
from ...shader.shader_node_elements import add, sub, mul, exp2

def __F_Schlick( inputs ):
    #{ f0, f90, dotVH } = inputs
    f0 = inputs['f0']
    f90 = inputs['f90']
    dotVH = inputs['dotVH']
	#Original approximation by Christophe Schlick '94
	#float fresnel = pow( 1.0 - dotVH, 5.0 );
	#Optimized variant (presented by Epic at SIGGRAPH '13)
	#https://cdn2.unrealengine.com/Resources/files/2013SiggraphPresentationsNotes-26915738.pdf
    fresnel = exp2( mul( sub( mul( - 5.55473, dotVH ), 6.98316 ), dotVH ) )
    return add( mul( f0, sub( 1.0, fresnel ) ), mul( f90, fresnel ) )
    
F_Schlick = ShaderNode( __F_Schlick)  # validated