from ..objects import LineSegments
from ..materials import LineBasicMaterial
from ..core import Float32BufferAttribute, BufferGeometry
from ..math import Color, Vector3, Matrix4

_vector = Vector3()
_boneMatrix = Matrix4()
_matrixWorldInv = Matrix4()

class SkeletonHelper(LineSegments):

    def __init__(self, object):
        
        bones = _getBoneList( object )
        geometry = BufferGeometry()
        
        vertices = []
        colors = []

        color1 = Color( 0, 0, 1 )
        color2 = Color( 0, 1, 0 )

        for bone in bones:
            if bone.parent and bone.parent.isBone:
                vertices.append( 0 )
                vertices.append( 0 )
                vertices.append( 0 )

                vertices.append( 0 )
                vertices.append( 0 )
                vertices.append( 0 )

                # color1.setHSL( 0.6, 0.5, 0.5 )
                # color2.setHSL( 0.6, 0.5, 0.5 )

                colors.extend( [ color1.r, color1.g, color1.b ] )
                colors.extend( [ color2.r, color2.g, color2.b ] )

        geometry.setAttribute( 'position', Float32BufferAttribute( vertices, 3 ) )
        geometry.setAttribute( 'color', Float32BufferAttribute( colors, 3 ) )

        material = LineBasicMaterial( { 'vertexColors': True, 'depthTest': False, 'depthWrite': False, 'toneMapped': False, 'transparent': True } )

        super().__init__( geometry, material )

        self.root = object
        self.bones = bones

        self.matrix = object.matrixWorld
        self.matrixAutoUpdate = False

    def updateMatrixWorld( self, force ):
        bones = self.bones
        geometry = self.geometry
        position = geometry.getAttribute( 'position' )

        _matrixWorldInv.copy( self.root.matrixWorld ).invert()

        j = 0
        for bone in bones:
            if bone.parent and bone.parent.isBone:
                _boneMatrix.multiplyMatrices( _matrixWorldInv, bone.matrixWorld )
                _vector.setFromMatrixPosition( _boneMatrix )
                position.setXYZ( j, _vector.x, _vector.y, _vector.z )

                _boneMatrix.multiplyMatrices( _matrixWorldInv, bone.parent.matrixWorld )
                _vector.setFromMatrixPosition( _boneMatrix )
                position.setXYZ( j + 1, _vector.x, _vector.y, _vector.z )

                j += 2

        geometry.getAttribute( 'position' ).needsUpdate = True

        super().updateMatrixWorld( force )


def _getBoneList( object ):

    boneList = []

    if object.isBone:
        boneList.append( object )

    for c in object.children:
        boneList.extend( _getBoneList( c ) )

    return boneList