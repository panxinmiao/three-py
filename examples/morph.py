import math, time
import numpy as np
import three
import three.nodes
from three.nodes import positionLocal, buffer, vertexIndex, element, add, bypass, skinning, modelViewProjection, uint
from wgpu.gui.auto import WgpuCanvas, run
from imgui_bundle import imgui
from wgpu.utils.imgui import ImguiRenderer

getMorph = three.nodes.FunctionNode('''
    fn getMorph( tex: texture_3d<f32>, vertex_index: u32, morph_index: u32 ) -> vec4<f32> {
        let y = vertex_index / u32(2048);
        let x = vertex_index - y * u32(2048);
        let morphUV = vec3<i32>( i32(x), i32(y), i32(morph_index) );
        return textureLoad( tex, morphUV, 0 );
    }
''')

class MorphMaterial(three.nodes.MeshNormalNodeMaterial):

    def __init__(self, parameters = None):
        super().__init__(parameters)


    def constructPosition(self, builder, stack):
        object = builder.object

        vertex = positionLocal

        if self.morphTexture:
            morphTextureNode = three.nodes.UniformNode( self.morphTexture, '3dTexture' )
            morphTargetInfluences = object.morphTargetInfluencesBuffer
            # morphTargetInfluences = buffer(influences, 'float', len(influences))
            for i in range(len(object.morphTargetInfluences)):
                morph = getMorph({"tex": morphTextureNode, "vertex_index": vertexIndex, "morph_index": uint(i)})
                # morphPosition = storage(geometry.morphAttributes.position[i], 'vec3', geometry.morphAttributes.position[i].count)
                morphWeight = element(morphTargetInfluences, uint(i)).x
                stack.assign(vertex, add(vertex, morph * morphWeight))


        if object.isSkinnedMesh == True:
            vertex = bypass( vertex, skinning( object ) )

        builder.context.vertex = vertex

        return modelViewProjection()


def createGeometry():
    geometry = three.BoxGeometry( 2, 2, 2, 32, 32, 32 )

    # create an empty array to hold targets for the attribute we want to morph
    # morphing positions and normals is supported
    geometry.morphAttributes.position = []

    # the original positions of the cube's vertices
    positionAttribute = geometry.attributes.position

    # for the first morph target we'll move the cube's vertices onto the surface of a sphere
    spherePositions = []

    # for the second morph target, we'll twist the cubes vertices
    twistPositions = []

    direction = three.Vector3( 1, 0, 0 )
    vertex = three.Vector3()

    _temp = three.Vector3()

    for i in range(positionAttribute.count):
        x = positionAttribute.getX( i )
        y = positionAttribute.getY( i )
        z = positionAttribute.getZ( i )

        spherePositions.extend([
            x * math.sqrt( 1 - ( y * y / 2 ) - ( z * z / 2 ) + ( y * y * z * z / 3 ) ) - x,
            y * math.sqrt( 1 - ( z * z / 2 ) - ( x * x / 2 ) + ( z * z * x * x / 3 ) ) - y,
            z * math.sqrt( 1 - ( x * x / 2 ) - ( y * y / 2 ) + ( x * x * y * y / 3 ) ) - z,
        ])

        # stretch along the x-axis so we can see the twist better
        vertex.set( x * 2, y, z )
        _temp.set( x, y, z)
        vertex.applyAxisAngle( direction, math.pi * x / 2 ).sub(_temp).toArray( twistPositions, len(twistPositions) )


    # add the spherical positions as the first morph target
    geometry.morphAttributes.position.append( three.Float32BufferAttribute( spherePositions, 3 ) )

    # add the twisted positions as the second morph target
    geometry.morphAttributes.position.append( three.Float32BufferAttribute( twistPositions, 3 ) )

    return geometry


def generateMorphTargetsTexture( geometry ):
    morphAttributes = geometry.morphAttributes

    textureWidth = 2048
    verticesCount = geometry.attributes.position.count
    textureHight = math.ceil( verticesCount / textureWidth )

    # only position now
    morphPositions = morphAttributes.position
    morphCount = len(morphPositions)

    data = np.zeros((morphCount, textureWidth * textureHight, 4), dtype=np.float32)
    for i in range(morphCount):
        position = np.array(morphPositions[i].array, dtype=np.float32).reshape(-1, 3)

        position = np.pad(position, ((0, 0), (0, 1)), 'constant')

        position = np.pad(position, ((0, textureWidth * textureHight - position.shape[0]), (0, 0)), 'constant')

        data[i, :, :] = position
    

    texture = three.Data3DTexture(memoryview(data), textureWidth, textureHight, morphCount)
    texture.type = three.FloatType
    texture.needsUpdate = True
    return texture


canvas = WgpuCanvas(size=(640, 480), max_fps=60, title="wgpu_renderer")

renderer = three.WgpuRenderer(canvas, antialias = True)
renderer.init()

camera = three.PerspectiveCamera(45, 640 / 480, 0.01, 100)
camera.position.z = 10

scene = three.Scene()

geometry = createGeometry()
material = MorphMaterial()

three.OrbitControls(camera, canvas)

material.morphTexture = generateMorphTargetsTexture(geometry)

mesh = three.Mesh(geometry, material)

mesh.influences = three.Float32Array.allocate( len(mesh.morphTargetInfluences) * 4 ) # padding to 16 bytes

mesh.morphTargetInfluencesBuffer = buffer(mesh.influences, 'vec4', len(mesh.morphTargetInfluences))

# print(mesh.morphTargetInfluences)
# geometry.setAttribute("morphTargetInfluences", three.Float32Array(mesh.morphTargetInfluences))

scene.add(mesh)


def updateMorphTargetInfluencesTypedArray(morphTargetInfluences, influencesArray):
    for i in range(len(morphTargetInfluences)):
        influencesArray[i*4] = morphTargetInfluences[i]


gui_renderer = ImguiRenderer(renderer._device, canvas, render_target_format=renderer._color_format)

state = {
    "auto": True,
    "spherify": 0,
    "twist": 0,
}


def draw_imgui():
    imgui.new_frame()
    imgui.set_next_window_size((250, 0), imgui.Cond_.always)
    imgui.set_next_window_pos(
        (gui_renderer.backend.io.display_size.x - 250, 0), imgui.Cond_.always
    )
    is_expand, _ = imgui.begin(
        "Morph Targets",
        None,
        flags=imgui.WindowFlags_.no_move | imgui.WindowFlags_.no_resize,
    )
    if is_expand:
        _, state["auto"] = imgui.checkbox("animate", state["auto"])
        if state["auto"]:
            t = time.time()
            state["spherify"] = (math.sin(t)+1)/2
            state["twist"] = (math.cos(t+1)+1)/2
        _, state["spherify"] = imgui.slider_float("spherify", state["spherify"], 0, 1)
        _, state["twist"] = imgui.slider_float("twist", state["twist"], 0, 1)

    imgui.end()
    imgui.end_frame()
    imgui.render()
    return imgui.get_draw_data()


gui_renderer.set_gui(draw_imgui)

def loop():
    mesh.morphTargetInfluences[ 0 ] = state["spherify"]
    mesh.morphTargetInfluences[ 1 ] = state["twist"]
    updateMorphTargetInfluencesTypedArray(mesh.morphTargetInfluences, mesh.influences)

    renderer.render(scene, camera)
    gui_renderer.render()

renderer.setAnimationLoop(loop)

if __name__ == '__main__':
    run()


