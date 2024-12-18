import three
import three.nodes
from pathlib import Path
from wgpu.gui.auto import WgpuCanvas, run

from loaders.texture_loader import TextureLoader, CubeTextureLoader


canvas = WgpuCanvas(size=(640, 480), max_fps=60, title="wgpu_renderer")

render = three.WgpuRenderer(canvas, antialias=True)
render.init()

camera = three.PerspectiveCamera(45, 640 / 480, 0.1, 10000)
camera.position.z = 300
scene = three.Scene()

dirLight = three.DirectionalLight(0xffffff, intensity=3.0)
dirLight.position.set(3, 0, 1).normalize()
scene.add(dirLight)

# scene.add(three.AmbientLight(0x111111))

texture_loader = TextureLoader(Path(__file__).parent / "textures", encoding=three.sRGBEncoding)

earth_geometry = three.SphereGeometry(63.71, 100, 50)

earth_material = three.MeshPhongMaterial(
    specular = 0x111111,
    shininess = 10,
    map=texture_loader.load("planets/earth_atmos_4096.jpg", flip=True),
    specularMap = texture_loader.load( 'planets/earth_specular_2048.jpg', flip=True),
    normalMap = texture_loader.load( 'planets/earth_normal_2048.jpg', flip=True),
    emissive = 0x808060,
    emissiveMap = texture_loader.load( 'planets/earth_lights_2048.png', flip=True),
    normalScale = three.Vector2( 0.85, - 0.85 )
)

earth_mesh = three.Mesh(earth_geometry, earth_material)
scene.add(earth_mesh)

earth_clouds_material = three.MeshPhongMaterial(
    map=texture_loader.load("planets/earth_clouds_2048.png", flip=True),
    side = three.FrontSide,
    transparent = True
)

earth_clouds = three.Mesh(earth_geometry, earth_clouds_material)
earth_clouds.scale.set(1.005, 1.005, 1.005)
earth_clouds.rotation.z = 0.41
scene.add(earth_clouds)


env_text_path = Path(__file__).parent / "textures" / "cube" / "MilkyWay"
env_text_urls = ['dark-s_px.jpg', 'dark-s_nx.jpg',
                 'dark-s_py.jpg', 'dark-s_ny.jpg',
                 'dark-s_pz.jpg', 'dark-s_nz.jpg']


loader = CubeTextureLoader(env_text_path, encoding=three.sRGBEncoding)
env_texture = loader.load(env_text_urls)

scene.background = three.nodes.CubeTextureNode(env_texture)

render.outputEncoding = three.sRGBEncoding

three.OrbitControls(camera, canvas)

def on_resize(event):
    camera.aspect = event['width'] / event['height']
    camera.updateProjectionMatrix()

canvas.add_event_handler(on_resize, 'resize')

def loop():
    earth_mesh.rotation.y += 0.001
    earth_clouds.rotation.y += 1.25 * 0.001

    render.render(scene, camera)

render.setAnimationLoop(loop)


if __name__ == "__main__":
    run()
