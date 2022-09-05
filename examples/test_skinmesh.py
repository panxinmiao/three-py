import three, math, time, os
from wgpu.gui.auto import WgpuCanvas, run

''' 
    Vulkan backend does not support at present.
    For more information, see: https://github.com/gfx-rs/naga/pull/1820/commits/65f8750dbae95efd25d60189285269643e9bd453 
'''
os.environ["WGPU_BACKEND_TYPE"] = "D3D12"

def createGeometry( sizing ):
    geometry = three.CylinderGeometry( 5, 5, sizing.height, 8, sizing.segmentHeight, True )
    position = geometry.attributes.position

    vertex = three.Vector3()
    skinIndices = []
    skinWeights = []

    for i in range(position.count):
        vertex.fromBufferAttribute( position, i )

        y = ( vertex.y + sizing.halfHeight )

        skinIndex = math.floor( y / sizing.segmentHeight )
        skinWeight = ( y % sizing.segmentHeight ) / sizing.segmentHeight

        skinIndices.append( skinIndex )
        skinIndices.append( skinIndex+1 )
        skinIndices.append( 0 )
        skinIndices.append( 0 )

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
    material = three.MeshNormalMaterial()
    material.side = three.DoubleSide
    material.color = three.Color(0xaaee00)

    # flat shading
    material.flatShading = True

    # from three.nodes import add, mul, normalize, cross, dFdx, dFdy, positionView
    # colorNode = add(mul(normalize(cross(dFdx(positionView), dFdy(positionView))), 0.5), 0.5)
    # material.colorNode = colorNode

    mesh = three.SkinnedMesh(geometry, material)
    skeleton = three.Skeleton( bones )

    mesh.add( bones[ 0 ] )
    mesh.bind( skeleton )

    return mesh


def init():
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

    canvas = WgpuCanvas(size=(640, 480), max_fps=60, title="Skinmesh")

    render = three.WgpuRenderer(canvas, antialias = True)
    render.init()

    camera = three.PerspectiveCamera(75, 640 / 480, 0.1, 200 )
    camera.position.z = 30
    camera.position.y = 30

    scene = three.Scene()

    geometry = createGeometry( sizing )
    bones = createBones( sizing )
    mesh = createMesh( geometry, bones )

    mesh.scale.multiplyScalar( 1 )

    scene.add( mesh )
    skeleton = three.SkeletonHelper( mesh )

    scene.add( skeleton )

    three.OrbitControls(camera, canvas)

    def loop():
        t = time.time()
        for bone in mesh.skeleton.bones:
            bone.rotation.z = math.sin( t ) * 2 / len(mesh.skeleton.bones)
        render.render(scene, camera)

    render.setAnimationLoop(loop)

    run()

if __name__ == '__main__':
    init()

