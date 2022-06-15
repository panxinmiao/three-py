import three
from wgpu.gui.auto import WgpuCanvas, run
from pathlib import Path
from loaders.texture_loader import TextureLoader

canvas = WgpuCanvas(size=(640, 480), max_fps=60, title="wgpu_renderer")

render = three.WgpuRenderer(canvas, antialias=True)
render.init()

camera = three.PerspectiveCamera(70, 640 / 480, 0.01, 100)
camera.position.z = 10

scene = three.Scene()

textureLoader = TextureLoader(Path(__file__).parent)
map = textureLoader.load('textures/sprite1.png')

material = three.SpriteMaterial()
material.map = map

sprite = three.Sprite(material)

scene.add(sprite)
control = three.OrbitControls(camera, canvas)

def loop():
    sprite.rotation.x += 0.01
    sprite.rotation.y += 0.02
    render.render(scene, camera)


render.setAnimationLoop(loop)

if __name__ == '__main__':
    run()
