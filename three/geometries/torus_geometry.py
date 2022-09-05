from ..core import BufferGeometry
from ..core import Float32BufferAttribute
from ..math import Vector3
import math

class TorusGeometry(BufferGeometry):
    
    def __init__(self, radius = 1, tube = 0.4, radialSegments = 8, tubularSegments = 6, arc = math.pi * 2) -> None:
        super().__init__()

        self._type = 'TorusGeometry'

        self.parameters = {
            'radius': radius,
            'tube': tube,
            'radialSegments': radialSegments,
            'tubularSegments': tubularSegments,
            'arc': arc,
        }

        radialSegments = math.floor( radialSegments )
        tubularSegments = math.floor( tubularSegments )

        # buffers

        indices = []
        vertices = []
        normals = []
        uvs = []

        # helper variables

        center = Vector3()
        vertex = Vector3()
        normal = Vector3()

        # generate vertices, normals and uvs

        for j in range(radialSegments+1):
            for i in range(tubularSegments+1):

                u = i / tubularSegments * arc
                v = j / radialSegments * math.pi * 2

                # vertex

                vertex.x = ( radius + tube * math.cos( v ) ) * math.cos( u )
                vertex.y = ( radius + tube * math.cos( v ) ) * math.sin( u )
                vertex.z = tube * math.sin( v )

                vertices.extend([vertex.x, vertex.y, vertex.z])

                # normal

                center.x = radius * math.cos( u )
                center.y = radius * math.sin( u )
                normal.subVectors( vertex, center ).normalize()

                normals.extend([normal.x, normal.y, normal.z])

                # uv

                uvs.append( i / tubularSegments )
                uvs.append( j / radialSegments )
            
        # generate indices

        for j in range(1, radialSegments+1):
            for i in range(1, tubularSegments+1):

                # indices

                a = ( tubularSegments + 1 ) * j + i - 1
                b = ( tubularSegments + 1 ) * ( j - 1 ) + i - 1
                c = ( tubularSegments + 1 ) * ( j - 1 ) + i
                d = ( tubularSegments + 1 ) * j + i

                # faces

                indices.extend([a, b, d])
                indices.extend([b, c, d])

        # build geometry

        self.setIndex( indices )
        self.setAttribute( 'position', Float32BufferAttribute( vertices, 3 ) )
        self.setAttribute( 'normal', Float32BufferAttribute( normals, 3 ) )
        self.setAttribute( 'uv', Float32BufferAttribute( uvs, 2 ) )



