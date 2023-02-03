import three
from three.extra.model_loader import ModelLoader
import three.nodes
from pathlib import Path
from wgpu.gui.auto import WgpuCanvas, run

from loaders.texture_loader import CubeTextureLoader


def init_scene():

    canvas = WgpuCanvas(size=(640, 480), max_fps=60, title="wgpu_renderer")

    render = three.WgpuRenderer(canvas, antialias = True)
    render.init()

    camera = three.PerspectiveCamera(45, 640 / 480, 0.25, 20)
    camera.position.set(- 1.8, 0.6, 2.7)

    scene = three.Scene()

    env_text_path = Path(__file__).parent / "textures" / "cube" / "Park2"
    env_text_urls = ['posx.jpg', 'negx.jpg',
                     'posy.jpg', 'negy.jpg', 
                     'posz.jpg', 'negz.jpg']

    loader = CubeTextureLoader(env_text_path)

    env_texture = loader.load(env_text_urls, encoding=three.sRGBEncoding)
    env_texture.generateMipmaps = True

    scene.environment = three.nodes.CubeTextureNode(env_texture)

    scene.background = scene.environment

    gltf_path = Path(__file__).parent / "models" / "DamagedHelmet" / "glTF" / "DamagedHelmet.gltf"
    
    modelLoader = ModelLoader()
    meshes = modelLoader.loadGLTF(gltf_path)

    # meshes[0].geometry.computeTangents()  # optional: use tangent to compute normalMap
    scene.add(*meshes)

    render.toneMappingNode = three.nodes.ToneMappingNode(three.LinearToneMapping, 1)
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
    init_scene()
    run()
