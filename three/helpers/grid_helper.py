from ..objects import LineSegments
from ..materials import LineBasicMaterial
from ..core import Float32BufferAttribute, BufferGeometry
from ..math import Color

class GridHelper(LineSegments):

    def __init__(self, size = 10, divisions = 10, color1 = 0x444444, color2 = 0x888888):
        
        color1 = Color( color1 )
        color2 = Color( color2 )

        center = divisions / 2
        step = size / divisions
        halfSize = size / 2

        vertices = []
        colors = []

        i = 0
        k = -halfSize

        while i <= divisions:
            vertices.extend([-halfSize, 0, k, halfSize, 0, k])
            vertices.extend([k, 0, -halfSize, k, 0, halfSize])

            color = color1 if i == center else color2

            colors.extend([color.r, color.g, color.b])
            colors.extend([color.r, color.g, color.b])
            colors.extend([color.r, color.g, color.b])
            colors.extend([color.r, color.g, color.b])

            i += 1
            k += step
        

        geometry = BufferGeometry()
        geometry.setAttribute( 'position', Float32BufferAttribute( vertices, 3 ) )
        geometry.setAttribute( 'color', Float32BufferAttribute( colors, 3 ) )

        material = LineBasicMaterial( { 'vertexColors': True, 'toneMapped': False } )
        
        self._type = 'GridHelper'
        super().__init__( geometry, material )

    def dispose(self):
        self.geometry.dispose()
        self.material.dispose()