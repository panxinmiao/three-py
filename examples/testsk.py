import three, math

from wgpu.gui.auto import WgpuCanvas, run

canvas = WgpuCanvas(size=(640, 480), title="wgpu_renderer")

render = three.WgpuRenderer(canvas, parameters={'antialias': True})
render.init()

camera = three.PerspectiveCamera(70, 640 / 480, 0.01, 100 )
camera.position.z = 30

scene = three.Scene()


def createGeometry( sizing ):
    print(sizing)
    geometry = three.CylinderGeometry( 5, 5, sizing.height, 8, sizing.segmentHeight, True )
    position = geometry.attributes.position

    vertex = three.Vector3()
    skinIndices = []
    skinWeights = []

    for i in range(position.count):
        vertex.fromBufferAttribute( position, i )
        # skinIndices.append( three.Vector4(0, 0, 0, 0) )
        # skinWeights.append( three.Vector4(0, 0, 0, 0) )

        y = ( vertex.y + sizing.halfHeight )

        skinIndex = math.floor( y / sizing.segmentHeight )
        skinWeight = ( y % sizing.segmentHeight ) / sizing.segmentHeight

        #skinIndices.append( skinIndex, skinIndex + 1, 0, 0 )
        skinIndices.append( skinIndex )
        skinIndices.append( skinIndex+1 )
        skinIndices.append( 0 )
        skinIndices.append( 0 )

        #skinWeights.append( 1 - skinWeight, skinWeight, 0, 0 )
        skinWeights.append( 1 - skinWeight )
        skinWeights.append( skinWeight )
        skinWeights.append( 0 )
        skinWeights.append( 0 )

    geometry.setAttribute( 'skinIndex', three.Uint16BufferAttribute( skinIndices, 4 ) )
    geometry.setAttribute( 'skinWeight', three.Float32BufferAttribute( skinWeights, 4 ) )

    return geometry


def createBones( sizing ):

    bones = []

    prevBone = three.Bone()
    bones.append( prevBone )
    prevBone.position.y = - sizing.halfHeight

    for i in range(sizing.segmentCount):
        bone = three.Bone()
        bone.position.y = sizing.segmentHeight
        bones.append( bone )

        prevBone.add( bone )
        prevBone = bone

    return bones


def createMesh( geometry, bones ):
    print(bones)
    material = three.MeshNormalMaterial()
    material.side = three.DoubleSide

    #material.side = three.DoubleSide
    mesh = three.SkinnedMesh(geometry, material)
    skeleton = three.Skeleton( bones )

    mesh.add( bones[ 0 ] )
    mesh.bind( skeleton )

    return mesh


def initBones():
    segmentHeight = 8
    segmentCount = 4
    height = segmentHeight * segmentCount
    halfHeight = height * 0.5

    sizing = three.Dict({
        'segmentHeight': segmentHeight,
        'segmentCount': segmentCount,
        'height': height,
        'halfHeight': halfHeight
    })

    geometry = createGeometry( sizing )
    bones = createBones( sizing )
    mesh = createMesh( geometry, bones )

    mesh.scale.multiplyScalar( 1 )
    scene.add( mesh )

    control = three.OrbitControls(camera, canvas)






initBones()


def loop():
    render.render(scene, camera)

render.setAnimationLoop(loop)

run()