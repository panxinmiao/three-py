from ..core import BufferGeometry
from ..core import Float32BufferAttribute
from ..math import Vector3, Vector2
import math

class CircleGeometry(BufferGeometry):

    def __init__(self, radius = 1, segments = 8, thetaStart = 0, thetaLength = math.pi * 2) -> None:
        super().__init__()

        self.type = 'CircleGeometry'

        self.parameters = {
            'radius': radius,
            'segments': segments,
            'thetaStart': thetaStart,
            'thetaLength': thetaLength
        }

        segments = max( 3, segments )

		# buffers

        indices = []
        vertices = []
        normals = []
        uvs = []

		# helper variables

        vertex = Vector3()
        uv = Vector2()

		# center point

        vertices.extend( [0, 0, 0] )
        normals.extend( [0, 0, 1] )
        uvs.extend( [0.5, 0.5] )

        s = 0
        i = 3
        while( s <= segments ):
            segment = thetaStart + s / segments * thetaLength
            # vertex

            vertex.x = radius * math.cos( segment )
            vertex.y = radius * math.sin( segment )

            vertices.extend( [vertex.x, vertex.y, vertex.z] )

            # normal

            normals.extend( [0, 0, 1] )

            # uvs

            uv.x = ( vertices[ i ] / radius + 1 ) / 2
            uv.y = ( vertices[ i + 1 ] / radius + 1 ) / 2

            uvs.extend( [uv.x, uv.y] )

            s += 1
            i += 3

        # indices

        for i in range(1, segments+1):
            indices.extend( [i, i + 1, 0] )


        # build geometry

        self.setIndex( indices )
        self.setAttribute( 'position', Float32BufferAttribute( vertices, 3 ) )
        self.setAttribute( 'normal', Float32BufferAttribute( normals, 3 ) )
        self.setAttribute( 'uv', Float32BufferAttribute( uvs, 2 ) )