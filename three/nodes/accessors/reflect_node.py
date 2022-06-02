from ..core.node import Node
from ..shadernode.shader_node_base_elements import nodeObject, transformedNormalView, positionViewDirection, transformDirection, negate, reflect, vec3, cameraViewMatrix

class ReflectNode(Node):
    VECTOR = 'vector'
    CUBE = 'cube'

    def __init__(self, scope = CUBE) -> None:
        super().__init__( 'vec3' )
        self.scope = scope

    def getHash(self, *args, **kwargs):
        return f'reflect-{self.scope}'

    def construct(self, builder):
        scope = self.scope
        outputNode = None
        if scope == ReflectNode.VECTOR:
            reflectView = reflect( negate( positionViewDirection ), transformedNormalView )
            reflectVec = transformDirection(reflectView, cameraViewMatrix)
            outputNode = reflectVec

        elif scope == ReflectNode.CUBE:
            reflectVec = nodeObject( ReflectNode( ReflectNode.VECTOR ) )
            cubeUV = vec3( negate( reflectVec.x ), reflectVec.yz )
            outputNode = cubeUV

        return outputNode

    def serialize( self, data ):
        super().serialize( data )
        data.scope = self.scope


    def deserialize( self, data ):
        super().deserialize( data )
        self.scope = data.scope

