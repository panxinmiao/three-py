from ..core.temp_node import TempNode
from ..core.node_builder import NodeBuilder
from ..accessors.model_node import ModelNode

from ..shadernode.shader_node import ShaderNode
from ..shadernode.shader_node_base_elements import positionView, normalView, uv, vec3, add, sub, mul, dFdx, dFdy, cross, max, dot, normalize, inversesqrt, faceDirection, modelNormalMatrix, TBNViewMatrix 

import three

def __perturbNormal2ArbNode(inputs):

    eye_pos = inputs['eye_pos']
    surf_norm = inputs['surf_norm']
    mapN = inputs['mapN']
    uv = inputs['uv']

    q0 = dFdx( eye_pos.xyz )
    q1 = dFdy( eye_pos.xyz )
    st0 = dFdx( uv.st )
    st1 = dFdy( uv.st )

    N = surf_norm; # normalized

    q1perp = cross( q1, N )
    q0perp = cross( N, q0 )

    T = add( mul( q1perp, st0.x ), mul( q0perp, st1.x ) )
    B = add( mul( q1perp, st0.y ), mul( q0perp, st1.y ) )

    det = max( dot( T, T ), dot( B, B ) )
    # scale = cond( equal( det, 0 ), 0, mul( faceDirection, inversesqrt( det ) ) )
    scale = mul(faceDirection, inversesqrt(det))

    return normalize( add( mul( T, mul( mapN.x, scale ) ), mul( B, mul( mapN.y, scale ) ), mul( N, mapN.z ) ) )

perturbNormal2ArbNode = ShaderNode(__perturbNormal2ArbNode)

class NormalMapNode(TempNode):

    def __init__(self, node, scaleNode = None) -> None:
        super().__init__('vec3')

        self.node = node
        self.scaleNode = scaleNode
        self.normalMapType = three.TangentSpaceNormalMap

    def construct(self, builder):

        # type = self.getNodeType( builder )

        normalMapType = self.normalMapType
        scaleNode = self.scaleNode

        normalOP = mul( self.node, 2.0 )
        normalMap = sub( normalOP, 1.0 )

        if scaleNode is not None:
            normalMapScale = mul( normalMap.xy, scaleNode )
            normalMap = vec3( normalMapScale, normalMap.z )

        outputNode = None

        if normalMapType == three.ObjectSpaceNormalMap:
            outputNode = normalize( mul(modelNormalMatrix, normalMap) )

        elif normalMapType == three.TangentSpaceNormalMap:
            
            if builder.hasGeometryAttribute('tangent'):
                outputNode = normalize( mul( TBNViewMatrix, normalMap ) )
            else:
                outputNode = perturbNormal2ArbNode({
                    'eye_pos': positionView,
                    'surf_norm': normalView,
                    'mapN': normalMap,
                    'uv': uv()
                } )
        
        return outputNode

