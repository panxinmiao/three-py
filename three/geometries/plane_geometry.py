from ..core import BufferGeometry
from ..core import Float32BufferAttribute
import math

class PlaneGeometry(BufferGeometry):

    def __init__(self, width = 1, height = 1, widthSegments = 1, heightSegments = 1) -> None:
        super().__init__()
        self.type = 'PlaneGeometry'

        self.parameters = {
            'width': width,
            'height': height,
            'widthSegments': widthSegments,
            'heightSegments': heightSegments
        }

        width_half = width / 2
        height_half = height / 2

        gridX = math.floor( widthSegments )
        gridY = math.floor( heightSegments )

        gridX1 = gridX + 1
        gridY1 = gridY + 1

        segment_width = width / gridX
        segment_height = height / gridY

        #

        indices = []
        vertices = []
        normals = []
        uvs = []

        for iy in range(gridY1):
            y = iy * segment_height - height_half
            for ix in range(gridX1):
                x = ix * segment_width - width_half

                vertices.extend( [x, - y, 0] )
                normals.extend( [0, 0, 1] )
                uvs.append( ix / gridX )
                uvs.append( 1 - ( iy / gridY ) )
            
        for iy in range(gridY):
            for ix in range(gridX):
                a = ix + gridX1 * iy
                b = ix + gridX1 * ( iy + 1 )
                c = ( ix + 1 ) + gridX1 * ( iy + 1 )
                d = ( ix + 1 ) + gridX1 * iy

                indices.extend( [a, b, d] )
                indices.extend( [b, c, d] )

        
        self.setIndex( indices )
        self.setAttribute( 'position', Float32BufferAttribute( vertices, 3 ) )
        self.setAttribute( 'normal', Float32BufferAttribute( normals, 3 ) )
        self.setAttribute( 'uv', Float32BufferAttribute( uvs, 2 ) )