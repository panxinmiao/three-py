from ..core.node import Node
from ..shadernode.shader_node_base_elements import transformedNormalView, positionViewDirection, transformDirection, negate, reflect, cameraViewMatrix

class ReflectVectorNode(Node):
    def __init__(self) -> None:
        super().__init__( 'vec3' )


    def getHash(self, *args ):
        return 'reflectVector'


    def construct(self, builder):
        reflectView = reflect( negate( positionViewDirection ), transformedNormalView )
        return transformDirection( reflectView, cameraViewMatrix )
