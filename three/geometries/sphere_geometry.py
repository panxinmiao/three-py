from ..core import BufferGeometry
from ..core import Float32BufferAttribute
from ..math import Vector3
import math

class SphereGeometry(BufferGeometry):

    def __init__(self, radius = 1, widthSegments = 32, heightSegments = 16, phiStart = 0, phiLength = math.pi * 2, thetaStart = 0, thetaLength = math.pi ) -> None:
        super().__init__()

        self.parameters = {
            'radius': radius,
            'widthSegments': widthSegments,
            'heightSegments': heightSegments,
            'phiStart': phiStart,
            'phiLength': phiLength,
            'thetaStart': thetaStart,
            'thetaLength': thetaLength
        }

        widthSegments = max( 3, math.floor( widthSegments ) )
        heightSegments = max( 2, math.floor( heightSegments ) )

        thetaEnd = min( thetaStart + thetaLength, math.pi )

        index = 0
        grid = []

        vertex = Vector3()
        normal = Vector3()

        # buffers

        indices = []
        vertices = []
        normals = []
        uvs = []

        # generate vertices, normals and uvs

        for iy in range(heightSegments+1):
            verticesRow = []
            v = iy / heightSegments

            # special case for the poles

            uOffset = 0

            if iy == 0 and thetaStart == 0:

                uOffset = 0.5 / widthSegments

            elif iy == heightSegments and thetaEnd == math.pi:

                uOffset = - 0.5 / widthSegments

            for ix in range(widthSegments+1):

                u = ix / widthSegments
                # vertex
                vertex.x = - radius * math.cos( phiStart + u * phiLength ) * math.sin( thetaStart + v * thetaLength )
                vertex.y = radius * math.cos( thetaStart + v * thetaLength )
                vertex.z = radius * math.sin( phiStart + u * phiLength ) * math.sin( thetaStart + v * thetaLength )

                vertices.extend( [vertex.x, vertex.y, vertex.z] )

                # normal
                normal.copy( vertex ).normalize()
                normals.extend( [normal.x, normal.y, normal.z] )

                # uv
                uvs.extend( [u + uOffset, 1 - v] )
                verticesRow.append( index )
                index += 1

            grid.append( verticesRow )

        # indices
        for iy in range(heightSegments):
            for ix in range(widthSegments):
                a = grid[iy][ix+1]
                b = grid[iy][ix]
                c = grid[iy+1][ix]
                d = grid[iy+1][ix+1]

                if iy != 0 or thetaStart > 0:
                    indices.extend( [a, b, d] )
                if iy != heightSegments - 1 or thetaEnd < math.pi:
                    indices.extend( [b, c, d] )

        # build geometry

        self.setIndex( indices )
        self.setAttribute( 'position', Float32BufferAttribute( vertices, 3 ) )
        self.setAttribute( 'normal', Float32BufferAttribute( normals, 3 ) )
        self.setAttribute( 'uv', Float32BufferAttribute( uvs, 2 ) )
