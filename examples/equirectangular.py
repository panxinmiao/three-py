import three
import three.nodes
from pathlib import Path
from wgpu.gui.auto import WgpuCanvas, run

from loaders.texture_loader import TextureLoader, RGBELoader

canvas = WgpuCanvas(size=(640, 480), max_fps=60, title="wgpu_renderer")

render = three.WgpuRenderer(canvas, antialias = True)
render.init()

camera = three.PerspectiveCamera(45, 640 / 480, 0.25, 20)
camera.position.z = 1


loader = TextureLoader(Path(__file__).parent / "textures")

# equirectTexture = loader.load("equirectMap.jpg", encoding=three.sRGBEncoding)
# equirectTexture.minFilter = three.LinearFilter

# use RGBELoader to load HDR texture
loader.imageLoader = RGBELoader()
equirectTexture = loader.load("royal_esplanade_1k.hdr")

equirectTexture.mapping = three.EquirectangularReflectionMapping

render.outputEncoding = three.sRGBEncoding

scene = three.Scene()
# scene.background = three.nodes.texture(equirectTexture, three.nodes.equirectUV(), 0)
scene.background = equirectTexture

controls = three.OrbitControls(camera, canvas)
controls.autoRotate = True
controls.rotateSpeed = -0.125
controls.autoRotateSpeed = 1.0


def loop():
    controls.update()
    render.render(scene, camera)

render.setAnimationLoop(loop)

if __name__ == '__main__':
    run()
