import three
import three.nodes
from pathlib import Path
from wgpu.gui.auto import WgpuCanvas, run

from loaders.texture_loader import TextureLoader, CubeTextureLoader


canvas = WgpuCanvas(size=(640, 480), max_fps=60, title="wgpu_renderer")

render = three.WgpuRenderer(canvas, antialias=True)
render.init()

camera = three.PerspectiveCamera(45, 640 / 480, 0.25, 2000)
camera.position.z = 500
scene = three.Scene()

dirLight = three.DirectionalLight(0xffffff)
dirLight.position.set(- 1, 0, 1).normalize()
scene.add(dirLight)

texture_loader = TextureLoader(Path(__file__).parent / "textures")

earth_geometry = three.SphereGeometry(63, 100, 50)

earth_material = three.MeshStandardMaterial(
    map=texture_loader.load("planets/earth_atmos_2048.jpg"),
)

earth_mesh = three.Mesh(earth_geometry, earth_material)
scene.add(earth_mesh)

earth_clouds_material = three.MeshStandardMaterial(
    map=texture_loader.load("planets/earth_clouds_2048.png"),
    transparent = True
)

earth_clouds = three.Mesh(earth_geometry, earth_clouds_material)
earth_clouds.scale.set(1.005, 1.005, 1.005)
scene.add(earth_clouds)


env_text_path = Path(__file__).parent / "textures" / "cube" / "MilkyWay"
env_text_urls = ['dark-s_px.jpg', 'dark-s_nx.jpg',
                 'dark-s_py.jpg', 'dark-s_ny.jpg',
                 'dark-s_pz.jpg', 'dark-s_nz.jpg']


loader = CubeTextureLoader(env_text_path)
env_texture = loader.load(env_text_urls)
env_texture.generateMipmaps = True

scene.background = three.nodes.CubeTextureNode(env_texture)

scene.environmentNode = scene.background

render.outputEncoding = three.sRGBEncoding

three.OrbitControls(camera, canvas)

def on_resize(event):
    camera.aspect = event['width'] / event['height']
    camera.updateProjectionMatrix()

canvas.add_event_handler(on_resize, 'resize')

def loop():
    render.render(scene, camera)

render.setAnimationLoop(loop)


if __name__ == "__main__":
    run()
