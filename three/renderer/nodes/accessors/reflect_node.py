from ..core.node import Node
from ..shader import nodeObject, normalWorld, positionWorld, cameraPosition, sub, normalize, join, negate, reflect

class ReflectNode(Node):
    VECTOR = 'vector'
    CUBE = 'cube'

    def __init__(self, scope = CUBE) -> None:
        super().__init__( 'vec3' )
        self.scope = scope

    def getHash(self, *args, **kwargs):
        return f'reflect-${self.scope}'

    def generate(self, builder):
        scope = self.scope

        if scope == ReflectNode.VECTOR:
            cameraToFrag = normalize( sub( positionWorld, cameraPosition ) )
            reflectVec = reflect( cameraToFrag, normalWorld )

            return reflectVec.build( builder )

        elif scope == ReflectNode.CUBE:
            reflectVec = nodeObject( ReflectNode( ReflectNode.VECTOR ) )
            cubeUV = join( negate( reflectVec.x ), reflectVec.yz )

            return cubeUV.build( builder )


    def serialize( self, data ):
        super().serialize( data )
        data.scope = self.scope


    def deserialize( self, data ):
        super().deserialize( data )
        self.scope = data.scope

