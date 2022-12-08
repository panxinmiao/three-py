from ..core.node import Node
from ..shadernode.shader_node_base_elements import transformedNormalView, positionViewDirection, transformDirection, negate, refract, cameraViewMatrix, materialReference

class RefractVectorNode(Node):
    def __init__(self) -> None:
        super().__init__( 'vec3' )


    def getHash(self, *args ):
        return 'refractVector'


    def construct(self, builder):
        refractView = refract( negate( positionViewDirection ), transformedNormalView, materialReference("refractionRatio", "float") )
        return transformDirection( refractView, cameraViewMatrix )
