import three, math, time
import three.nodes
from wgpu.gui.auto import WgpuCanvas, run

canvas = WgpuCanvas(size=(640, 480), max_fps=60, title="Light Test")

render = three.WgpuRenderer(canvas, antialias = True)
render.init()

camera = three.PerspectiveCamera(70, 640 / 480, 0.1, 10)
camera.position.z = 2

scene = three.Scene()
#scene.background = three.Color( 0x111111 )

geometry = three.SphereGeometry(0.02, 16, 8)

light1 = three.PointLight( 0xffaa00, 2, 1 )
light1.add( three.Mesh( geometry, three.MeshBasicMaterial( { 'color': 0xffaa00 } ) ) )
scene.add( light1 )

light2 = three.PointLight( 0x0040ff, 2, 1 )
light2.add( three.Mesh( geometry, three.MeshBasicMaterial( { 'color': 0x0040ff } ) ) )
scene.add( light2 )

light3 = three.PointLight( 0x80ff80, 2, 1 )
light3.add( three.Mesh( geometry, three.MeshBasicMaterial( { 'color': 0x80ff80 } ) ) )
scene.add( light3 )

allLightsNode = three.nodes.LightsNode().fromLights( [ light1, light2, light3 ] )

points = []

for i in range(3000):
    point = three.Vector3().random().subScalar( 0.5 ).multiplyScalar( 2 )
    points.append( point )


geometryPoints = three.BufferGeometry().setFromPoints( points )

materialPoints =  three.nodes.PointsNodeMaterial()


def _light_model(inputs, *args):
    inputs["reflectedLight"].directDiffuse.add( inputs["lightColor"] )

customLightingModel = three.nodes.ShaderNode(_light_model)

lightingModelContext = three.nodes.ContextNode(allLightsNode, {"lightingModelNode": {"direct": customLightingModel} })
materialPoints.lightsNode = lightingModelContext

pointCloud = three.Points( geometryPoints, materialPoints )

scene.add( pointCloud )

three.OrbitControls(camera, canvas)

def loop():
    t = time.time() * 0.5
    scale = 0.5

    light1.position.x = math.sin( t * 0.7 ) * scale
    light1.position.y = math.cos( t * 0.5 ) * scale
    light1.position.z = math.cos( t * 0.3 ) * scale

    light2.position.x = math.cos( t * 0.3 ) * scale
    light2.position.y = math.sin( t * 0.5 ) * scale
    light2.position.z = math.sin( t * 0.7 ) * scale

    light3.position.x = math.sin( t * 0.7 ) * scale
    light3.position.y = math.cos( t * 0.3 ) * scale
    light3.position.z = math.sin( t * 0.5 ) * scale

    render.render(scene, camera)

render.setAnimationLoop(loop)

if __name__ == '__main__':
    run()


