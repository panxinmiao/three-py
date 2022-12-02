from ..objects import LineSegments
from ..materials import LineBasicMaterial
from ..core import Float32BufferAttribute, BufferGeometry
from ..math import Color

class AxesHelper(LineSegments):

    def __init__(self, size = 1):
        
        vertices = [
            0, 0, 0,    size, 0, 0,
            0, 0, 0,    0, size, 0,
            0, 0, 0,    0, 0, size
        ]

        colors = [
            1, 0, 0,    1, 0.6, 0,
            0, 1, 0,    0.6, 1, 0,
            0, 0, 1,    0, 0.6, 1
        ]

        geometry = BufferGeometry()
        geometry.setAttribute( 'position', Float32BufferAttribute( vertices, 3 ) )
        geometry.setAttribute( 'color', Float32BufferAttribute( colors, 3 ) )

        material = LineBasicMaterial( { 'vertexColors': True, 'toneMapped': False } )
        
        self._type = 'AxesHelper'
        super().__init__( geometry, material )

    
    def setColors(self, xAxisColor, yAxisColor, zAxisColor ):
        color = Color()
        array = self.geometry.attributes.color.array

        color.set( xAxisColor )
        color.toArray( array, 0 )
        color.toArray( array, 3 )

        color.set( yAxisColor )
        color.toArray( array, 6 )
        color.toArray( array, 9 )

        color.set( zAxisColor )
        color.toArray( array, 12 )
        color.toArray( array, 15 )

        self.geometry.attributes.color.needsUpdate = True

        return self

    def dispose(self):
        self.geometry.dispose()
        self.material.dispose()