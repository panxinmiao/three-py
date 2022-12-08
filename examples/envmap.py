import time, math
import three
import three.nodes
from pathlib import Path
from wgpu.gui.auto import WgpuCanvas, run

from loaders.texture_loader import CubeTextureLoader

canvas = WgpuCanvas(size=(640, 480), title="materials")
renderer = three.WgpuRenderer(canvas, antialias=True)
renderer.init()

camera = three.PerspectiveCamera(45, 640 / 480, 0.1, 2500)
camera.position.set(0, 400, 1200)
scene = three.Scene()



# Lights

scene.add(three.AmbientLight(0x222222))
directional_light = three.DirectionalLight(0xFFFFFF, 2)
directional_light.position.set(1, 1, 1)
scene.add(directional_light)
point_light = three.PointLight(0xFFFFFF, 2, decay=0)
scene.add(point_light)

# light_helper = three.PointLightHelper(point_light, size=4)
# scene.add(light_helper)


env_map_path = Path(__file__).parent / "textures" / "cube" / "Park2"
env_map_urls = ["posx.jpg", "negx.jpg", "posy.jpg", "negy.jpg", "posz.jpg", "negz.jpg"]


loader = CubeTextureLoader(env_map_path)
envMap = loader.load(env_map_urls, encoding=three.sRGBEncoding)
envMap.generateMipmaps = True

scene.background = three.nodes.CubeTextureNode(envMap)
scene.environment = scene.background

refractMap = three.nodes.CubeTextureNode(envMap, three.nodes.refractVector)

geometry = three.TeapotGeometry( 80, 18 )

basicMaterial = three.MeshBasicMaterial()
basicMaterial.envMap = refractMap

mesh = three.Mesh(geometry, three.MeshBasicMaterial())
mesh.position.set(-300, 0, 0)
scene.add(mesh)

mesh = three.Mesh(geometry, three.MeshBasicMaterial(envMap = refractMap))
mesh.position.set(-300, 300, 0)
scene.add(mesh)


mesh = three.Mesh(geometry, three.MeshStandardMaterial(roughness=0.1, metalness=1.0))
scene.add(mesh)

standardMaterial = three.MeshStandardMaterial(
    roughness=0.1, metalness=1.0, 
    envMap=three.nodes.CubeTextureNode(envMap, three.nodes.refractVector, 0) # force sampling from LOD 0
)
mesh = three.Mesh(geometry, standardMaterial)
mesh.position.set(0, 300, 0)
scene.add(mesh)


mesh = three.Mesh(geometry, three.MeshPhongMaterial(shininess=30))
mesh.position.set(300, 0, 0)
scene.add(mesh)

mesh = three.Mesh(geometry, three.MeshPhongMaterial(shininess=30, envMap=refractMap))
mesh.position.set(300, 300, 0)
scene.add(mesh)

renderer.outputEncoding = three.sRGBEncoding

three.OrbitControls(camera, canvas)

def on_resize(event):
    camera.aspect = event['width'] / event['height']
    camera.updateProjectionMatrix()

canvas.add_event_handler(on_resize, 'resize')

def animate():
    timer = time.time() * 0.25

    point_light.position.x = math.sin(timer * 7) * 300
    point_light.position.y = math.cos(timer * 5) * 400
    point_light.position.z = math.cos(timer * 3) * 300

    renderer.render(scene, camera)


renderer.setAnimationLoop(animate)

if __name__ == "__main__":
    run()