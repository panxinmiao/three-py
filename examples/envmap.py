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
directional_light = three.DirectionalLight(0xFFFFFF, 1)
directional_light.position.set(1, 1, 1)
scene.add(directional_light)
point_light = three.PointLight(0xFFFFFF, 2)
scene.add(point_light)

# light_helper = three.PointLightHelper(point_light, size=4)
# scene.add(light_helper)


env_map_path = Path(__file__).parent / "textures" / "cube" / "Park2"
env_map_urls = ["posx.jpg", "negx.jpg", "posy.jpg", "negy.jpg", "posz.jpg", "negz.jpg"]


loader = CubeTextureLoader(env_map_path)
envMap = loader.load(env_map_urls, encoding=three.sRGBEncoding)
envMap.generateMipmaps = True

scene.background = three.nodes.CubeTextureNode(envMap)

scene.environmentNode = scene.background


cube_width = 400
numbers_per_side = 2
sphere_radius = (cube_width / numbers_per_side) * 0.8 * 0.5
step_size = 1.0 / numbers_per_side

geometry = three.SphereGeometry(sphere_radius, 32, 16)

basicMaterial = three.MeshBasicMaterial(color=0x0099FF)
# basicMaterial.envMap = envMap

mesh = three.Mesh(geometry, basicMaterial)

mesh.position.set(-200, 0, 0)
scene.add(mesh)

standardMaterial = three.MeshStandardMaterial(color=0x0099FF)
standardMaterial.roughness = 0.1
standardMaterial.metalness = 1.0
standardMaterial.envMap = envMap

mesh2 = three.Mesh(geometry, standardMaterial)

scene.add(mesh2)

phongMaterial = three.MeshPhongMaterial(color=0x0099FF, shininess=100)
phongMaterial.envMap = envMap

mesh3 = three.Mesh(geometry, phongMaterial)

mesh3.position.set(200, 0, 0)
scene.add(mesh3)

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