from ..core import BufferGeometry
from ..core import BufferAttribute
from ..structure import Uint32Array, Float32Array
from ..math import Vector3, Matrix4, Vector4
import math

class TeapotGeometry(BufferGeometry):

    def __init__(self, size = 50, segments = 10, bottom = True, lid = True, body = True, fitLid = True, blinn = True) -> None:
        
        super().__init__()

        # 32 * 4 * 4 Bezier spline patches
        teapotPatches = [
            # rim
            0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
            3, 16, 17, 18, 7, 19, 20, 21, 11, 22, 23, 24, 15, 25, 26, 27,
            18, 28, 29, 30, 21, 31, 32, 33, 24, 34, 35, 36, 27, 37, 38, 39,
            30, 40, 41, 0, 33, 42, 43, 4, 36, 44, 45, 8, 39, 46, 47, 12,
            # body
            12, 13, 14, 15, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59,
            15, 25, 26, 27, 51, 60, 61, 62, 55, 63, 64, 65, 59, 66, 67, 68,
            27, 37, 38, 39, 62, 69, 70, 71, 65, 72, 73, 74, 68, 75, 76, 77,
            39, 46, 47, 12, 71, 78, 79, 48, 74, 80, 81, 52, 77, 82, 83, 56,
            56, 57, 58, 59, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95,
            59, 66, 67, 68, 87, 96, 97, 98, 91, 99, 100, 101, 95, 102, 103, 104,
            68, 75, 76, 77, 98, 105, 106, 107, 101, 108, 109, 110, 104, 111, 112, 113,
            77, 82, 83, 56, 107, 114, 115, 84, 110, 116, 117, 88, 113, 118, 119, 92,
            # handle
            120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135,
            123, 136, 137, 120, 127, 138, 139, 124, 131, 140, 141, 128, 135, 142, 143, 132,
            132, 133, 134, 135, 144, 145, 146, 147, 148, 149, 150, 151, 68, 152, 153, 154,
            135, 142, 143, 132, 147, 155, 156, 144, 151, 157, 158, 148, 154, 159, 160, 68,
            # spout
            161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176,
            164, 177, 178, 161, 168, 179, 180, 165, 172, 181, 182, 169, 176, 183, 184, 173,
            173, 174, 175, 176, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196,
            176, 183, 184, 173, 188, 197, 198, 185, 192, 199, 200, 189, 196, 201, 202, 193,
            # lid
            203, 203, 203, 203, 204, 205, 206, 207, 208, 208, 208, 208, 209, 210, 211, 212,
            203, 203, 203, 203, 207, 213, 214, 215, 208, 208, 208, 208, 212, 216, 217, 218,
            203, 203, 203, 203, 215, 219, 220, 221, 208, 208, 208, 208, 218, 222, 223, 224,
            203, 203, 203, 203, 221, 225, 226, 204, 208, 208, 208, 208, 224, 227, 228, 209,
            209, 210, 211, 212, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240,
            212, 216, 217, 218, 232, 241, 242, 243, 236, 244, 245, 246, 240, 247, 248, 249,
            218, 222, 223, 224, 243, 250, 251, 252, 246, 253, 254, 255, 249, 256, 257, 258,
            224, 227, 228, 209, 252, 259, 260, 229, 255, 261, 262, 233, 258, 263, 264, 237,
            # bottom
            265, 265, 265, 265, 266, 267, 268, 269, 270, 271, 272, 273, 92, 119, 118, 113,
            265, 265, 265, 265, 269, 274, 275, 276, 273, 277, 278, 279, 113, 112, 111, 104,
            265, 265, 265, 265, 276, 280, 281, 282, 279, 283, 284, 285, 104, 103, 102, 95,
            265, 265, 265, 265, 282, 286, 287, 266, 285, 288, 289, 270, 95, 94, 93, 92
        ]

        teapotVertices = [
            1.4, 0, 2.4,
            1.4, - 0.784, 2.4,
            0.784, - 1.4, 2.4,
            0, - 1.4, 2.4,
            1.3375, 0, 2.53125,
            1.3375, - 0.749, 2.53125,
            0.749, - 1.3375, 2.53125,
            0, - 1.3375, 2.53125,
            1.4375, 0, 2.53125,
            1.4375, - 0.805, 2.53125,
            0.805, - 1.4375, 2.53125,
            0, - 1.4375, 2.53125,
            1.5, 0, 2.4,
            1.5, - 0.84, 2.4,
            0.84, - 1.5, 2.4,
            0, - 1.5, 2.4,
            - 0.784, - 1.4, 2.4,
            - 1.4, - 0.784, 2.4,
            - 1.4, 0, 2.4,
            - 0.749, - 1.3375, 2.53125,
            - 1.3375, - 0.749, 2.53125,
            - 1.3375, 0, 2.53125,
            - 0.805, - 1.4375, 2.53125,
            - 1.4375, - 0.805, 2.53125,
            - 1.4375, 0, 2.53125,
            - 0.84, - 1.5, 2.4,
            - 1.5, - 0.84, 2.4,
            - 1.5, 0, 2.4,
            - 1.4, 0.784, 2.4,
            - 0.784, 1.4, 2.4,
            0, 1.4, 2.4,
            - 1.3375, 0.749, 2.53125,
            - 0.749, 1.3375, 2.53125,
            0, 1.3375, 2.53125,
            - 1.4375, 0.805, 2.53125,
            - 0.805, 1.4375, 2.53125,
            0, 1.4375, 2.53125,
            - 1.5, 0.84, 2.4,
            - 0.84, 1.5, 2.4,
            0, 1.5, 2.4,
            0.784, 1.4, 2.4,
            1.4, 0.784, 2.4,
            0.749, 1.3375, 2.53125,
            1.3375, 0.749, 2.53125,
            0.805, 1.4375, 2.53125,
            1.4375, 0.805, 2.53125,
            0.84, 1.5, 2.4,
            1.5, 0.84, 2.4,
            1.75, 0, 1.875,
            1.75, - 0.98, 1.875,
            0.98, - 1.75, 1.875,
            0, - 1.75, 1.875,
            2, 0, 1.35,
            2, - 1.12, 1.35,
            1.12, - 2, 1.35,
            0, - 2, 1.35,
            2, 0, 0.9,
            2, - 1.12, 0.9,
            1.12, - 2, 0.9,
            0, - 2, 0.9,
            - 0.98, - 1.75, 1.875,
            - 1.75, - 0.98, 1.875,
            - 1.75, 0, 1.875,
            - 1.12, - 2, 1.35,
            - 2, - 1.12, 1.35,
            - 2, 0, 1.35,
            - 1.12, - 2, 0.9,
            - 2, - 1.12, 0.9,
            - 2, 0, 0.9,
            - 1.75, 0.98, 1.875,
            - 0.98, 1.75, 1.875,
            0, 1.75, 1.875,
            - 2, 1.12, 1.35,
            - 1.12, 2, 1.35,
            0, 2, 1.35,
            - 2, 1.12, 0.9,
            - 1.12, 2, 0.9,
            0, 2, 0.9,
            0.98, 1.75, 1.875,
            1.75, 0.98, 1.875,
            1.12, 2, 1.35,
            2, 1.12, 1.35,
            1.12, 2, 0.9,
            2, 1.12, 0.9,
            2, 0, 0.45,
            2, - 1.12, 0.45,
            1.12, - 2, 0.45,
            0, - 2, 0.45,
            1.5, 0, 0.225,
            1.5, - 0.84, 0.225,
            0.84, - 1.5, 0.225,
            0, - 1.5, 0.225,
            1.5, 0, 0.15,
            1.5, - 0.84, 0.15,
            0.84, - 1.5, 0.15,
            0, - 1.5, 0.15,
            - 1.12, - 2, 0.45,
            - 2, - 1.12, 0.45,
            - 2, 0, 0.45,
            - 0.84, - 1.5, 0.225,
            - 1.5, - 0.84, 0.225,
            - 1.5, 0, 0.225,
            - 0.84, - 1.5, 0.15,
            - 1.5, - 0.84, 0.15,
            - 1.5, 0, 0.15,
            - 2, 1.12, 0.45,
            - 1.12, 2, 0.45,
            0, 2, 0.45,
            - 1.5, 0.84, 0.225,
            - 0.84, 1.5, 0.225,
            0, 1.5, 0.225,
            - 1.5, 0.84, 0.15,
            - 0.84, 1.5, 0.15,
            0, 1.5, 0.15,
            1.12, 2, 0.45,
            2, 1.12, 0.45,
            0.84, 1.5, 0.225,
            1.5, 0.84, 0.225,
            0.84, 1.5, 0.15,
            1.5, 0.84, 0.15,
            - 1.6, 0, 2.025,
            - 1.6, - 0.3, 2.025,
            - 1.5, - 0.3, 2.25,
            - 1.5, 0, 2.25,
            - 2.3, 0, 2.025,
            - 2.3, - 0.3, 2.025,
            - 2.5, - 0.3, 2.25,
            - 2.5, 0, 2.25,
            - 2.7, 0, 2.025,
            - 2.7, - 0.3, 2.025,
            - 3, - 0.3, 2.25,
            - 3, 0, 2.25,
            - 2.7, 0, 1.8,
            - 2.7, - 0.3, 1.8,
            - 3, - 0.3, 1.8,
            - 3, 0, 1.8,
            - 1.5, 0.3, 2.25,
            - 1.6, 0.3, 2.025,
            - 2.5, 0.3, 2.25,
            - 2.3, 0.3, 2.025,
            - 3, 0.3, 2.25,
            - 2.7, 0.3, 2.025,
            - 3, 0.3, 1.8,
            - 2.7, 0.3, 1.8,
            - 2.7, 0, 1.575,
            - 2.7, - 0.3, 1.575,
            - 3, - 0.3, 1.35,
            - 3, 0, 1.35,
            - 2.5, 0, 1.125,
            - 2.5, - 0.3, 1.125,
            - 2.65, - 0.3, 0.9375,
            - 2.65, 0, 0.9375,
            - 2, - 0.3, 0.9,
            - 1.9, - 0.3, 0.6,
            - 1.9, 0, 0.6,
            - 3, 0.3, 1.35,
            - 2.7, 0.3, 1.575,
            - 2.65, 0.3, 0.9375,
            - 2.5, 0.3, 1.125,
            - 1.9, 0.3, 0.6,
            - 2, 0.3, 0.9,
            1.7, 0, 1.425,
            1.7, - 0.66, 1.425,
            1.7, - 0.66, 0.6,
            1.7, 0, 0.6,
            2.6, 0, 1.425,
            2.6, - 0.66, 1.425,
            3.1, - 0.66, 0.825,
            3.1, 0, 0.825,
            2.3, 0, 2.1,
            2.3, - 0.25, 2.1,
            2.4, - 0.25, 2.025,
            2.4, 0, 2.025,
            2.7, 0, 2.4,
            2.7, - 0.25, 2.4,
            3.3, - 0.25, 2.4,
            3.3, 0, 2.4,
            1.7, 0.66, 0.6,
            1.7, 0.66, 1.425,
            3.1, 0.66, 0.825,
            2.6, 0.66, 1.425,
            2.4, 0.25, 2.025,
            2.3, 0.25, 2.1,
            3.3, 0.25, 2.4,
            2.7, 0.25, 2.4,
            2.8, 0, 2.475,
            2.8, - 0.25, 2.475,
            3.525, - 0.25, 2.49375,
            3.525, 0, 2.49375,
            2.9, 0, 2.475,
            2.9, - 0.15, 2.475,
            3.45, - 0.15, 2.5125,
            3.45, 0, 2.5125,
            2.8, 0, 2.4,
            2.8, - 0.15, 2.4,
            3.2, - 0.15, 2.4,
            3.2, 0, 2.4,
            3.525, 0.25, 2.49375,
            2.8, 0.25, 2.475,
            3.45, 0.15, 2.5125,
            2.9, 0.15, 2.475,
            3.2, 0.15, 2.4,
            2.8, 0.15, 2.4,
            0, 0, 3.15,
            0.8, 0, 3.15,
            0.8, - 0.45, 3.15,
            0.45, - 0.8, 3.15,
            0, - 0.8, 3.15,
            0, 0, 2.85,
            0.2, 0, 2.7,
            0.2, - 0.112, 2.7,
            0.112, - 0.2, 2.7,
            0, - 0.2, 2.7,
            - 0.45, - 0.8, 3.15,
            - 0.8, - 0.45, 3.15,
            - 0.8, 0, 3.15,
            - 0.112, - 0.2, 2.7,
            - 0.2, - 0.112, 2.7,
            - 0.2, 0, 2.7,
            - 0.8, 0.45, 3.15,
            - 0.45, 0.8, 3.15,
            0, 0.8, 3.15,
            - 0.2, 0.112, 2.7,
            - 0.112, 0.2, 2.7,
            0, 0.2, 2.7,
            0.45, 0.8, 3.15,
            0.8, 0.45, 3.15,
            0.112, 0.2, 2.7,
            0.2, 0.112, 2.7,
            0.4, 0, 2.55,
            0.4, - 0.224, 2.55,
            0.224, - 0.4, 2.55,
            0, - 0.4, 2.55,
            1.3, 0, 2.55,
            1.3, - 0.728, 2.55,
            0.728, - 1.3, 2.55,
            0, - 1.3, 2.55,
            1.3, 0, 2.4,
            1.3, - 0.728, 2.4,
            0.728, - 1.3, 2.4,
            0, - 1.3, 2.4,
            - 0.224, - 0.4, 2.55,
            - 0.4, - 0.224, 2.55,
            - 0.4, 0, 2.55,
            - 0.728, - 1.3, 2.55,
            - 1.3, - 0.728, 2.55,
            - 1.3, 0, 2.55,
            - 0.728, - 1.3, 2.4,
            - 1.3, - 0.728, 2.4,
            - 1.3, 0, 2.4,
            - 0.4, 0.224, 2.55,
            - 0.224, 0.4, 2.55,
            0, 0.4, 2.55,
            - 1.3, 0.728, 2.55,
            - 0.728, 1.3, 2.55,
            0, 1.3, 2.55,
            - 1.3, 0.728, 2.4,
            - 0.728, 1.3, 2.4,
            0, 1.3, 2.4,
            0.224, 0.4, 2.55,
            0.4, 0.224, 2.55,
            0.728, 1.3, 2.55,
            1.3, 0.728, 2.55,
            0.728, 1.3, 2.4,
            1.3, 0.728, 2.4,
            0, 0, 0,
            1.425, 0, 0,
            1.425, 0.798, 0,
            0.798, 1.425, 0,
            0, 1.425, 0,
            1.5, 0, 0.075,
            1.5, 0.84, 0.075,
            0.84, 1.5, 0.075,
            0, 1.5, 0.075,
            - 0.798, 1.425, 0,
            - 1.425, 0.798, 0,
            - 1.425, 0, 0,
            - 0.84, 1.5, 0.075,
            - 1.5, 0.84, 0.075,
            - 1.5, 0, 0.075,
            - 1.425, - 0.798, 0,
            - 0.798, - 1.425, 0,
            0, - 1.425, 0,
            - 1.5, - 0.84, 0.075,
            - 0.84, - 1.5, 0.075,
            0, - 1.5, 0.075,
            0.798, - 1.425, 0,
            1.425, - 0.798, 0,
            0.84, - 1.5, 0.075,
            1.5, - 0.84, 0.075
        ]

        # number of segments per patch
        segments = max( 2, math.floor( segments ) )

        # Jim Blinn scaled the teapot down in size by about 1.3 for
        # some rendering tests. He liked the new proportions that he kept
        # the data in this form. The model was distributed with these new
        # proportions and became the norm. Trivia: comparing images of the
        # real teapot and the computer model, the ratio for the bowl of the
        # real teapot is more like 1.25, but since 1.3 is the traditional
        # value given, we use it here.
        blinnScale = 1.3

        # scale the size to be the real scaling factor
        maxHeight = 3.15 * ( 1 if blinn else blinnScale )

        maxHeight2 = maxHeight / 2
        trueSize = size / maxHeight2

        # Number of elements depends on what is needed. Subtract degenerate
        # triangles at tip of bottom and lid out in advance.
        numTriangles = ( 8 * segments - 4 ) * segments if bottom else 0
        numTriangles += ( 16 * segments - 4 ) * segments if lid else 0
        numTriangles += 40 * segments * segments if body else 0

        indices = Uint32Array( numTriangles * 3 )
        numVertices = 4 if bottom else 0
        numVertices += 8 if lid else 0
        numVertices += 20 if body else 0
        numVertices *= ( segments + 1 ) * ( segments + 1 )

        vertices = Float32Array( numVertices * 3 )
        normals = Float32Array( numVertices * 3 )
        uvs = Float32Array( numVertices * 2 )

        # Bezier form
        ms = Matrix4()
        ms.set(
            - 1.0, 3.0, - 3.0, 1.0,
            3.0, - 6.0, 3.0, 0.0,
            - 3.0, 3.0, 0.0, 0.0,
            1.0, 0.0, 0.0, 0.0 )
        
        g = [0, 0, 0, 0,
            0, 0, 0, 0,
            0, 0, 0, 0,
            0, 0, 0, 0]

        sp = [0, 0, 0, 0]
        tp = [0, 0, 0, 0]
        dsp = [0, 0, 0, 0]
        dtp = [0, 0, 0, 0]

        # M * G * M matrix, sort of see
		# http://www.cs.helsinki.fi/group/goa/mallinnus/curves/surfaces.html
        mgm = [Matrix4(), Matrix4(), Matrix4()]

        vert = [0, 0, 0]
        sdir = [0, 0, 0]
        tdir = [0, 0, 0]

        norm = Vector3()

        # tcoord = None

        # sval = None
        # tval = None
        # p = None
        # dsval = 0
        # dtval = 0

        normOut = Vector3()

        gmx = Matrix4()
        tmtx = Matrix4()

        vsp = Vector4()
        vtp = Vector4()
        vdsp = Vector4()
        vdtp = Vector4()

        vsdir = Vector3()
        vtdir = Vector3()

        mst = ms.clone().transpose()

        # internal function: test if triangle has any matching vertices;
        # if so, don't save triangle, since it won't display anything.
        def notDegenerate( vtx1, vtx2, vtx3 ): # if any vertex matches, return false
            return not (
                (
                    ( vertices[ vtx1 * 3 ] == vertices[ vtx2 * 3 ] ) and
                    ( vertices[ vtx1 * 3 + 1 ] == vertices[ vtx2 * 3 + 1 ] ) and
                    ( vertices[ vtx1 * 3 + 2 ] == vertices[ vtx2 * 3 + 2 ] ) 
                ) or
                (
                    ( vertices[ vtx1 * 3 ] == vertices[ vtx3 * 3 ] ) and
                    ( vertices[ vtx1 * 3 + 1 ] == vertices[ vtx3 * 3 + 1 ] ) and
                    ( vertices[ vtx1 * 3 + 2 ] == vertices[ vtx3 * 3 + 2 ] )
                ) or
                (
                    ( vertices[ vtx2 * 3 ] == vertices[ vtx3 * 3 ] ) and
                    ( vertices[ vtx2 * 3 + 1 ] == vertices[ vtx3 * 3 + 1 ] ) and
                    ( vertices[ vtx2 * 3 + 2 ] == vertices[ vtx3 * 3 + 2 ] )
                )
            )

        minPatches = 0 if body else 20
        maxPatches = 32 if bottom else 28

        vertPerRow = segments + 1

        surfCount = 0

        vertCount = 0
        normCount = 0
        uvCount = 0

        indexCount = 0

        for surf in range(minPatches, maxPatches):
            # lid is in the middle of the data, patches 20-27,
            # so ignore it for this part of the loop if the lid is not desired
            if lid or ( surf < 20 or surf >= 28):

                # get M * G * M matrix for x,y,z
                for i in range(3):

                    # get control patches
                    for r in range(4):
                        for c in range(4):
                            # transposed
                            g[ c * 4 + r ] = teapotVertices[ teapotPatches[ surf * 16 + r * 4 + c ] * 3 + i ]

                            # is the lid to be made larger, and is this a point on the lid
                            # that is X or Y?
                            if fitLid and ( surf >= 20 and surf < 28 ) and ( i != 2 ):

                                # increase XY size by 7.7%, found empirically. I don't
                                # increase Z so that the teapot will continue to fit in the
                                # space -1 to 1 for Y (Y is up for the final model).
                                g[ c * 4 + r ] *= 1.077

                            # Blinn "fixed" the teapot by dividing Z by blinnScale, and that's the
                            # data we now use. The original teapot is taller. Fix it:
                            if not blinn and ( i == 2 ):
                                g[ c * 4 + r ] *= blinnScale

                    gmx.set( g[ 0 ], g[ 1 ], g[ 2 ], g[ 3 ], g[ 4 ], g[ 5 ], g[ 6 ], g[ 7 ], g[ 8 ], g[ 9 ], g[ 10 ], g[ 11 ], g[ 12 ], g[ 13 ], g[ 14 ], g[ 15 ] )

                    tmtx.multiplyMatrices( gmx, ms )
                    mgm[ i ].multiplyMatrices( mst, tmtx )

                # step along, get points, and output
                for sstep in range(segments+1):
                    s = sstep / segments

                    for tstep in range(segments+1):
                        t = tstep / segments

                        # point from basis
						# get power vectors and their derivatives
                        p = 3
                        sval = 1.0
                        tval = 1.0

                        while p>=0:
                            sp[p] = sval
                            tp[p] = tval
                            sval *= s
                            tval *= t

                            if p == 3:
                                dsp[ p ] = 0.0
                                dtp[ p ] = 0.0
                                dsval = 1.0
                                dtval = 1.0
                            else:
                                dsp[ p ] = dsval * ( 3 - p )
                                dtp[ p ] = dtval * ( 3 - p )
                                dsval *= s
                                dtval *= t
                            
                            p -= 1

                        vsp.fromArray( sp )
                        vtp.fromArray( tp )
                        vdsp.fromArray( dsp )
                        vdtp.fromArray( dtp )

                        for i in range(3):

                            # multiply power vectors times matrix to get value
                            tcoord = vsp.clone()
                            tcoord.applyMatrix4( mgm[ i ] )
                            vert[ i ] = tcoord.dot( vtp )

                            # get s and t tangent vectors
                            tcoord = vdsp.clone()
                            tcoord.applyMatrix4( mgm[ i ] )
                            sdir[ i ] = tcoord.dot( vtp )

                            tcoord = vsp.clone()
                            tcoord.applyMatrix4( mgm[ i ] )
                            tdir[ i ] = tcoord.dot( vdtp )

                        # find normal
                        vsdir.fromArray( sdir )
                        vtdir.fromArray( tdir )
                        norm.crossVectors( vtdir, vsdir )
                        norm.normalize()

                        # if X and Z length is 0, at the cusp, so point the normal up or down, depending on patch number
                        if vert[ 0 ] == 0 and vert[ 1 ] == 0:
                            # if above the middle of the teapot, normal points up, else down
                            normOut.set( 0, 1 if vert[ 2 ] > maxHeight2 else - 1, 0 )
                        else:
                            # standard output: rotate on X axis
                            normOut.set( norm.x, norm.z, - norm.y )

                        # store it all
                        vertices[ vertCount ] = trueSize * vert[ 0 ]
                        vertCount += 1
                        vertices[ vertCount ] = trueSize * ( vert[ 2 ] - maxHeight2 )
                        vertCount += 1
                        vertices[ vertCount ] = - trueSize * vert[ 1 ]
                        vertCount += 1

                        normals[ normCount ] = normOut.x
                        normCount += 1
                        normals[ normCount ] = normOut.y
                        normCount += 1
                        normals[ normCount ] = normOut.z
                        normCount += 1

                        uvs[ uvCount ] = 1 - t
                        uvCount += 1
                        uvs[ uvCount ] = 1 - s
                        uvCount += 1

                # save the faces
                for sstep in range(segments):
                    for tstep in range(segments):
                        v1 = surfCount * vertPerRow * vertPerRow + sstep * vertPerRow + tstep
                        v2 = v1 + 1
                        v3 = v2 + vertPerRow
                        v4 = v1 + vertPerRow

                        # Normals and UVs cannot be shared. Without clone(), you can see the consequences
						# of sharing if you call geometry.applyMatrix4( matrix ).
                        if notDegenerate(v1, v2, v3):
                            indices[ indexCount ] = v1
                            indexCount+=1
                            indices[ indexCount ] = v2
                            indexCount+=1
                            indices[ indexCount ] = v3
                            indexCount+=1
                        
                        if notDegenerate(v1, v3, v4):
                            indices[ indexCount ] = v1
                            indexCount+=1
                            indices[ indexCount ] = v3
                            indexCount+=1
                            indices[ indexCount ] = v4
                            indexCount+=1
                
                surfCount += 1
        
        self.setIndex( BufferAttribute( indices, 1 ) )
        self.setAttribute( 'position', BufferAttribute( vertices, 3 ) )
        self.setAttribute( 'normal', BufferAttribute( normals, 3 ) )
        self.setAttribute( 'uv', BufferAttribute( uvs, 2 ) )

        self.computeBoundingSphere()