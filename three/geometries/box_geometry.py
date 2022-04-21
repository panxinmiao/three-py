from ..core import BufferGeometry
from ..core import Float32BufferAttribute
from ..math import Vector3
import math

class BoxGeometry(BufferGeometry):
    
    def __init__(self, width = 1, height = 1, depth = 1, widthSegments = 1, heightSegments = 1, depthSegments = 1) -> None:
        super().__init__()

        self._type = 'BoxGeometry'

        self.parameters = {
            width: width,
            height: height,
            depth: depth,
            widthSegments: widthSegments,
            heightSegments: heightSegments,
            depthSegments: depthSegments
        }

        scope = self

        # segments

        widthSegments = math.floor( widthSegments )
        heightSegments = math.floor( heightSegments )
        depthSegments = math.floor( depthSegments )

		# buffers

        indices = []
        vertices = []
        normals = []
        uvs = []

        # helper variables

        numberOfVertices = 0
        groupStart = 0



        def buildPlane( u, v, w, udir, vdir, width, height, depth, gridX, gridY, materialIndex ):
            nonlocal numberOfVertices
            nonlocal groupStart

            segmentWidth = width / gridX
            segmentHeight = height / gridY

            widthHalf = width / 2
            heightHalf = height / 2
            depthHalf = depth / 2

            gridX1 = gridX + 1
            gridY1 = gridY + 1

            vertexCounter = 0
            groupCount = 0

            vector = Vector3()

            # generate vertices, normals and uvs

            for iy in range(gridY1):
            # for ( let iy = 0 iy < gridY1 iy ++ ) {

                y = iy * segmentHeight - heightHalf

                for ix in range(gridX1):
                # for ( let ix = 0 ix < gridX1 ix ++ ) {

                    x = ix * segmentWidth - widthHalf

                    # set values to correct vector component
                    setattr(vector, u, x * udir)
                    setattr(vector, v, y * vdir)
                    setattr(vector, w, depthHalf)

                    # vector[u] = x * udir
                    # vector[v] = y * vdir
                    # vector[w] = depthHalf

                    # now apply vector to vertex buffer

                    vertices.extend( [vector.x, vector.y, vector.z] )

                    # set values to correct vector component

                    setattr(vector, u, 0)
                    setattr(vector, v, 0)
                    setattr(vector, w, 1 if depth > 0 else - 1)

                    # vector[u] = 0
                    # vector[v] = 0
                    # vector[w] = 1 if depth > 0 else - 1

                    # now apply vector to normal buffer

                    normals.extend( [vector.x, vector.y, vector.z] )

                    # uvs

                    uvs.append( ix / gridX )
                    uvs.append( 1 - ( iy / gridY ) )

                    # counters

                    vertexCounter += 1



			# indices

			# 1. you need three indices to draw a single face
			# 2. a single segment consists of two faces
			# 3. so we need to generate six (2*3) indices per segment

            for iy in range(gridY):
            # for ( let iy = 0 iy < gridY iy ++ ) {
                for ix in range(gridX):
                # for ( let ix = 0 ix < gridX ix ++ ) {

                    a = numberOfVertices + ix + gridX1 * iy
                    b = numberOfVertices + ix + gridX1 * ( iy + 1 )
                    c = numberOfVertices + ( ix + 1 ) + gridX1 * ( iy + 1 )
                    d = numberOfVertices + ( ix + 1 ) + gridX1 * iy

                    # faces

                    indices.extend( [a, b, d] )
                    indices.extend( [b, c, d] )

                    # increase counter

                    groupCount += 6


            # add a group to the geometry. this will ensure multi material support

            scope.addGroup( groupStart, groupCount, materialIndex )

            # calculate new start value for groups

            groupStart += groupCount

            # update total number of vertices

            numberOfVertices += vertexCounter


        # build each side of the box geometry

        buildPlane( 'z', 'y', 'x', - 1, - 1, depth, height, width, depthSegments, heightSegments, 0 ) # px
        buildPlane( 'z', 'y', 'x', 1, - 1, depth, height, - width, depthSegments, heightSegments, 1 ) # nx
        buildPlane( 'x', 'z', 'y', 1, 1, width, depth, height, widthSegments, depthSegments, 2 ) # py
        buildPlane( 'x', 'z', 'y', 1, - 1, width, depth, - height, widthSegments, depthSegments, 3 ) # ny
        buildPlane( 'x', 'y', 'z', 1, - 1, width, height, depth, widthSegments, heightSegments, 4 ) # pz
        buildPlane( 'x', 'y', 'z', - 1, - 1, width, height, - depth, widthSegments, heightSegments, 5 ) # nz

        # build geometry

        self.setIndex( indices )
        self.setAttribute( 'position', Float32BufferAttribute( vertices, 3 ) )
        self.setAttribute( 'normal', Float32BufferAttribute( normals, 3 ) )
        self.setAttribute( 'uv', Float32BufferAttribute( uvs, 2 ) )


        