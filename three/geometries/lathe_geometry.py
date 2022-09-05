import math
from ..core import BufferGeometry
from ..core import Float32BufferAttribute
from ..math import Vector3, Vector2
from ..math.math_utils import clamp

class LatheGeometry(BufferGeometry):

    def __init__(self, points = None, segments = 12, phiStart = 0, phiLength = math.pi * 2) -> None:
        super().__init__()

        points = points or [ Vector2( 0, - 0.5 ), Vector2( 0.5, 0 ), Vector2( 0, 0.5 ) ]

        self._type = 'LatheGeometry'

        self.parameters = {
            'points': points,
            'segments': segments,
            'phiStart': phiStart,
            'phiLength': phiLength,
        }

        segments = math.floor( segments )

        # clamp phiLength so it's in range of [ 0, 2PI ]
        phiLength = clamp( phiLength, 0, 2 * math.pi )

        # buffers
        indices = []
        vertices = []
        uvs = []
        initNormals = []
        normals = []

        # helper variables

        inverseSegments = 1.0 / segments
        vertex = Vector3()
        uv = Vector2()
        normal = Vector3()
        curNormal = Vector3()
        prevNormal = Vector3()
        dx = 0
        dy = 0

        pointsLength = len( points )

        # pre-compute normals for initial "meridian"

        for j in range(pointsLength):
            
            if j == 0:  # special handling for 1st vertex on path
                dx = points[ j + 1 ].x - points[ j ].x
                dy = points[ j + 1 ].y - points[ j ].y

                normal.x = dy * 1.0
                normal.y = - dx
                normal.z = dy * 0.0

                prevNormal.copy( normal )

                normal.normalize()

                initNormals.extend([normal.x, normal.y, normal.z])

            elif j == pointsLength -1:   # special handling for last Vertex on path
                initNormals.extend([prevNormal.x, prevNormal.y, prevNormal.z])

            else:   # default handling for all vertices in between
                dx = points[ j + 1 ].x - points[ j ].x
                dy = points[ j + 1 ].y - points[ j ].y

                normal.x = dy * 1.0
                normal.y = - dx
                normal.z = dy * 0.0

                curNormal.copy( normal )

                normal.x += prevNormal.x
                normal.y += prevNormal.y
                normal.z += prevNormal.z

                normal.normalize()

                initNormals.extend([normal.x, normal.y, normal.z])

                prevNormal.copy( curNormal )

        # generate vertices, uvs and normals

        for i in range(segments+1):
            phi = phiStart + i * inverseSegments * phiLength

            sin = math.sin( phi )
            cos = math.cos( phi )

            for j in range(pointsLength):
                # vertex

                vertex.x = points[ j ].x * sin
                vertex.y = points[ j ].y
                vertex.z = points[ j ].x * cos

                vertices.extend([vertex.x, vertex.y, vertex.z])

				# uv

                uv.x = i / segments
                uv.y = j / ( pointsLength - 1 )

                uvs.extend([uv.x, uv.y])

				# normal

                x = initNormals[ 3 * j + 0 ] * sin
                y = initNormals[ 3 * j + 1 ]
                z = initNormals[ 3 * j + 0 ] * cos

                normals.extend([x, y, z])

        # indices

        for i in range(segments):
            for j in range(pointsLength-1):

                base = j + i * pointsLength

                a = base
                b = base + pointsLength
                c = base + pointsLength + 1
                d = base + 1

                # faces

                indices.extend([a, b, d])
                indices.extend([c, d, b])

        # build geometry

        self.setIndex( indices )
        self.setAttribute( 'position', Float32BufferAttribute( vertices, 3 ) )
        self.setAttribute( 'normal', Float32BufferAttribute( normals, 3 ) )
        self.setAttribute( 'uv', Float32BufferAttribute( uvs, 2 ) )