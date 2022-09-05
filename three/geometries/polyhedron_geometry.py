from ..core import BufferGeometry
from ..core import Float32BufferAttribute
from ..math import Vector3, Vector2
import math

class PolyhedronGeometry(BufferGeometry):

    def __init__(self, vertices = None, indices = None, radius = 1, detail = 0) -> None:
        super().__init__()

        vertices = vertices or []
        indices = indices or []

        self._type = 'PolyhedronGeometry'

        self.parameters = {
            'vertices': vertices,
            'indices': indices,
            'radius': radius,
            'detail': detail
        }

        # default buffer data
        vertexBuffer = []
        uvBuffer = []

        # helper functions

        def subdivide( detail ):

            a = Vector3()
            b = Vector3()
            c = Vector3()

            # iterate over all faces and apply a subdivison with the given detail value

            for i in range( 0, len( indices ), 3 ):

                # get the vertices of the face

                getVertexByIndex( indices[ i + 0 ], a )
                getVertexByIndex( indices[ i + 1 ], b )
                getVertexByIndex( indices[ i + 2 ], c )

                # perform subdivision

                subdivideFace( a, b, c, detail )

        def subdivideFace( a:Vector3, b:Vector3, c:Vector3, detail ):
            cols = detail + 1

            # we use this multidimensional array as a data structure for creating the subdivision

            v = []

            # construct all of the vertices for this subdivision

            for i in range( cols + 1 ):
                v.append( [] )

                aj = a.clone().lerp( c, i / cols )
                bj = b.clone().lerp( c, i / cols )

                rows = cols - i

                for j in range( rows + 1 ):
                    if j == 0 and i == cols:
                        v[ i ].append( aj )
                    else:
                        v[ i ].append( aj.clone().lerp( bj, j / rows ) )
            
            # construct all of the faces

            for i in range( cols ):
                for j in range( 2 * ( cols - i ) - 1 ):
                    k = math.floor( j / 2 )

                    if j % 2 == 0:
                        pushVertex( v[ i ][ k + 1 ] )
                        pushVertex( v[ i + 1 ][ k ] )
                        pushVertex( v[ i ][ k ] )
                    else:
                        pushVertex( v[ i ][ k + 1 ] )
                        pushVertex( v[ i + 1 ][ k + 1 ] )
                        pushVertex( v[ i + 1 ][ k ] )

        def applyRadius( radius ):

            vertex = Vector3()

            for i in range( 0, len( vertexBuffer ), 3 ):
                #vertex.fromArray( vertexBuffer, i )
                vertex.x = vertexBuffer[ i + 0 ]
                vertex.y = vertexBuffer[ i + 1 ]
                vertex.z = vertexBuffer[ i + 2 ]

                vertex.normalize().multiplyScalar( radius )
                
                #vertex.toArray( vertexBuffer, i )
                vertexBuffer[ i + 0 ] = vertex.x
                vertexBuffer[ i + 1 ] = vertex.y
                vertexBuffer[ i + 2 ] = vertex.z

        def generateUVs():

            vertex = Vector3()

            for i in range( 0, len( vertexBuffer ), 3 ):

                #vertex.fromArray( vertexBuffer, i )
                vertex.x = vertexBuffer[ i + 0 ]
                vertex.y = vertexBuffer[ i + 1 ]
                vertex.z = vertexBuffer[ i + 2 ]

                u = azimuth( vertex ) / 2 / math.pi + 0.5
                v = inclination( vertex ) / math.pi + 0.5

                uvBuffer.append( u )
                uvBuffer.append( 1-v )

            correctUVs()
            correctSeam()

        def correctSeam():

            # handle case when face straddles the seam

            for i in range( 0, len( uvBuffer ), 6 ):
                # uv data of a single face

                x0 = uvBuffer[ i + 0 ]
                x1 = uvBuffer[ i + 2 ]
                x2 = uvBuffer[ i + 4 ]

                _max = max( x0, max( x1, x2 ) )
                _min = min( x0, min( x1, x2 ) )

                # 0.9 is somewhat arbitrary

                if _max > 0.9 and _min < 0.1:
                    if x0 < 0.2:
                        uvBuffer[ i + 0 ] += 1
                    if x1 < 0.2:
                        uvBuffer[ i + 2 ] += 1
                    if x2 < 0.2:
                        uvBuffer[ i + 4 ] += 1

        def pushVertex( vertex:Vector3 ):
            vertexBuffer.append( vertex.x )
            vertexBuffer.append( vertex.y )
            vertexBuffer.append( vertex.z )

        def getVertexByIndex( index, vertex:Vector3 ):
            stride = index * 3
            vertex.x = vertices[ stride + 0 ]
            vertex.y = vertices[ stride + 1 ]
            vertex.z = vertices[ stride + 2 ]

        def correctUVs():

            a = Vector3()
            b = Vector3()
            c = Vector3()

            centroid = Vector3()

            uvA = Vector2()
            uvB = Vector2()
            uvC = Vector2()

            i = 0
            j = 0

            while i< len(vertexBuffer):

                a.set(vertexBuffer[ i + 0 ], vertexBuffer[ i + 1 ], vertexBuffer[ i + 2 ])
                b.set(vertexBuffer[ i + 3 ], vertexBuffer[ i + 4 ], vertexBuffer[ i + 5 ])
                c.set(vertexBuffer[ i + 6 ], vertexBuffer[ i + 7 ], vertexBuffer[ i + 8 ])

                uvA.set( uvBuffer[ j + 0 ], uvBuffer[ j + 1 ] )
                uvB.set( uvBuffer[ j + 2 ], uvBuffer[ j + 3 ] )
                uvC.set( uvBuffer[ j + 4 ], uvBuffer[ j + 5 ] )

                centroid.copy( a ).add( b ).add( c ).divideScalar( 3 )

                azi = azimuth( centroid )

                correctUV( uvA, j + 0, a, azi )
                correctUV( uvB, j + 2, b, azi )
                correctUV( uvC, j + 4, c, azi )

                i += 9
                j += 6

        def correctUV( uv, stride, vector, azimuth):

            if ( azimuth < 0 and uv.x == 1 ):
                uvBuffer[ stride ] = uv.x - 1

            if ( vector.x == 0 and vector.z == 0 ):
                uvBuffer[ stride ] = azimuth / 2 / math.pi + 0.5

        def azimuth(vector):
            return math.atan2( vector.z, -vector.x )
        
        # Angle above the XZ plane
        def inclination(vector):
            return math.atan2( -vector.y, math.sqrt( ( vector.x * vector.x ) + ( vector.z * vector.z ) ) )

        
        # the subdivision creates the vertex buffer data

        subdivide( detail )

        # all vertices should lie on a conceptual sphere with a given radius

        applyRadius( radius )

        # finally, create the uv data

        generateUVs()

        # build non-indexed geometry

        self.setAttribute( 'position', Float32BufferAttribute( vertexBuffer, 3 ) )
        self.setAttribute( 'normal', Float32BufferAttribute( vertexBuffer.copy(), 3 ) )
        self.setAttribute( 'uv', Float32BufferAttribute( uvBuffer, 2 ) )

        if detail == 0:
            self.computeVertexNormals() # flat normals
        else:
            self.normalizeNormals() # smooth normals
