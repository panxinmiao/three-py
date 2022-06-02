from ..core import BufferGeometry
from ..core import Float32BufferAttribute
from ..math import Vector3, Vector2
import math


class CylinderGeometry(BufferGeometry):

    def __init__(self, radiusTop = 1, radiusBottom = 1, height = 1, radialSegments = 8, heightSegments = 1, openEnded = False, thetaStart = 0, thetaLength = math.pi * 2 ) -> None:
        super().__init__()

        self.parameters = {
            radiusTop: radiusTop,
            radiusBottom: radiusBottom,
            height: height,
            radialSegments: radialSegments,
            heightSegments: heightSegments,
            openEnded: openEnded,
            thetaStart: thetaStart,
            thetaLength: thetaLength
        }

        #scope = self

        radialSegments = math.floor( radialSegments )
        heightSegments = math.floor( heightSegments )

        # buffers

        indices = []
        vertices = []
        normals = []
        uvs = []

        # helper variables

        index = 0
        indexArray = []
        halfHeight = height / 2
        groupStart = 0


        def generateTorso():
            nonlocal index
            nonlocal groupStart

            normal = Vector3()
            vertex = Vector3()

            groupCount = 0

            # this will be used to calculate the normal
            slope = ( radiusBottom - radiusTop ) / height

            # generate vertices, normals and uvs

            for y in range( 0, heightSegments+1 ):
                indexRow = []
                v = y / heightSegments
                radius = v * ( radiusBottom - radiusTop ) + radiusTop

                for x in range( 0, radialSegments+1 ):
                    u = x / radialSegments
                    theta = u * thetaLength + thetaStart

                    sinTheta = math.sin( theta )
                    cosTheta = math.cos( theta )

                    vertex.x = radius * sinTheta
                    vertex.y = - v * height + halfHeight
                    vertex.z = radius * cosTheta

                    # vertex
                    vertices.append( vertex.x )
                    vertices.append( vertex.y )
                    vertices.append( vertex.z )

                    # normal
                    normal.set( sinTheta, slope, cosTheta ).normalize()
                    normals.append( normal.x )
                    normals.append( normal.y )
                    normals.append( normal.z )

                    # uv
                    uvs.append( u )
                    uvs.append( 1 - v )

                    # save index of vertex in respective row
                    indexRow.append( index  )
                    index += 1

                # now save vertices of the row in our index array
                indexArray.append( indexRow )

            # generate indices

            for x in range( radialSegments ):
                for y in range( heightSegments ):
                    # we use the index array to access the correct indices
                    a = indexArray[ y ][ x ]
                    b = indexArray[ y + 1 ][ x ]
                    c = indexArray[ y + 1 ][ x + 1 ]
                    d = indexArray[ y ][ x + 1 ]

                    # face one
                    indices.append( a )
                    indices.append( b )
                    indices.append( d )

                    # face two
                    indices.append( b )
                    indices.append( c )
                    indices.append( d )

                    # update group counter
                    groupCount += 6

            # add a group to the geometry. this will ensure multi material support
            self.addGroup( groupStart, groupCount, 0 )

            # calculate new start value for groups
            groupStart += groupCount

        def generateCap( top: bool ) -> None:
            nonlocal index
            nonlocal groupStart

            # save the index of the first center vertex
            centerIndexStart = index
            uv = Vector2()
            vertex = Vector3()

            groupCount = 0

            radius = radiusTop if top == True else radiusBottom
            sign = 1 if top == True else - 1

            # first we generate the center vertex data of the cap.
            # because the geometry needs one set of uvs per face,
            # we must generate a center vertex per face/segment

            for x in range( radialSegments+1 ):
                # vertex
                vertices.append( 0 )
                vertices.append( halfHeight * sign )
                vertices.append( 0 )

                # normal
                normals.append( 0 )
                normals.append( sign )
                normals.append( 0 )

                # uv
                uvs.append( 0.5 )
                uvs.append( 0.5 )

                # increase index
                index += 1

            # save the index of the last center vertex
            centerIndexEnd = index

            # now we generate the surrounding vertices, normals and uvs

            for x in range( radialSegments + 1 ):
                u = x / radialSegments
                theta = u * thetaLength + thetaStart

                cosTheta = math.cos( theta )
                sinTheta = math.sin( theta )

                # vertex
                vertex.x = radius * sinTheta
                vertex.y = halfHeight * sign
                vertex.z = radius * cosTheta

                vertices.append( vertex.x )
                vertices.append( vertex.y )
                vertices.append( vertex.z )

                # normal
                normals.append(0)
                normals.append(sign)
                normals.append(0)

                # uv
                uv.x = ( cosTheta * 0.5 ) + 0.5
                uv.y = ( sinTheta * 0.5 * sign ) + 0.5
                uvs.append( uv.x )
                uvs.append( uv.y )

                # increase index
                index += 1

            # generate indices
            for x in range( radialSegments ):

                c = centerIndexStart + x
                i = centerIndexEnd + x

                if top == True:
                    indices.append( i )
                    indices.append( i + 1 )
                    indices.append( c )
                else:
                    indices.append( i + 1 )
                    indices.append( i )
                    indices.append( c )

                groupCount += 3

            # add a group to the geometry. this will ensure multi material support

            self.addGroup( groupStart, groupCount, 1 if top == True else 2 )

            # calculate new start value for groups
            groupStart += groupCount

                # generate geometry

        generateTorso()

        if openEnded == False:
            if radiusTop > 0: 
                generateCap( True )
            if radiusBottom > 0: 
                generateCap( False )

        # build geometry

        self.setIndex( indices )
        self.setAttribute( 'position', Float32BufferAttribute( vertices, 3 ) )
        self.setAttribute( 'normal', Float32BufferAttribute( normals, 3 ) )
        self.setAttribute( 'uv', Float32BufferAttribute( uvs, 2 ) )