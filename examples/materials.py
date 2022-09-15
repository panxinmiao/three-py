import time, math
import three
import three.nodes
from colorsys import hls_to_rgb
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
directional_light.position.set(1, 1, 1).normalize()
scene.add(directional_light)
point_light = three.PointLight(0xFFFFFF, 2, 800)
scene.add(point_light)

# light_helper = three.PointLightHelper(point_light, size=4)
# scene.add(light_helper)


env_map_path = Path(__file__).parent / "textures" / "cube" / "Park2"
env_map_urls = ["posx.jpg", "negx.jpg", "posy.jpg", "negy.jpg", "posz.jpg", "negz.jpg"]


loader = CubeTextureLoader(env_map_path)
envMap = loader.load(env_map_urls)
envMap.generateMipmaps = True

scene.background = three.nodes.CubeTextureNode(envMap)


cube_width = 400
numbers_per_side = 2
sphere_radius = (cube_width / numbers_per_side) * 0.8 * 0.5
step_size = 1.0 / numbers_per_side

geometry = three.SphereGeometry(sphere_radius, 32, 16)

standardMaterial = three.MeshStandardMaterial(color=0x00FF00)
standardMaterial.envMap = envMap

mesh = three.Mesh(geometry, standardMaterial)

mesh.position.set(-100, 0, 0)
scene.add(mesh)

phongMaterial = three.MeshPhongMaterial(color=0x00FF00, shininess=50)
phongMaterial.envMap = envMap

mesh2 = three.Mesh(geometry, phongMaterial)

mesh2.position.set(100, 0, 0)
scene.add(mesh2)


# index = 0
# alpha = 0.0
# while alpha <= 1.0:
#     beta = 0.0
#     while beta <= 1.0:
#         gamma = 0.0
#         while gamma <= 1.0:
#             material = three.MeshStandardMaterial(
#                 color = three.Color(*hls_to_rgb(alpha, 0.5, gamma * 0.5 + 0.1)),
#                 metalness=beta,
#                 roughness=1.0 - alpha,
#             )

#             if index % 2 != 0:
#                 material.envMap = envMap

#             mesh = three.Mesh(geometry, material)

#             mesh.position.x = alpha * 400 - 200
#             mesh.position.y = beta * 400 - 200
#             mesh.position.z = gamma * 400 - 200
#             scene.add(mesh)
#             index += 1

#             gamma += step_size
#         beta += step_size
#     alpha += step_size


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