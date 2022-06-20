import time
import math
from random import random
import three
import three.nodes
from three.nodes import texture, uv, mul, float, color, userData
from wgpu.gui.auto import WgpuCanvas, run
from pathlib import Path

from loaders.texture_loader import TextureLoader
from utils.fps_recorder import FPSRecorder

canvas = WgpuCanvas(size=(640, 480), max_fps=60, title="wgpu_renderer")

render = three.WgpuRenderer(canvas, antialias=True)
render.init()

camera = three.PerspectiveCamera(70, 640 / 480, 0.01, 2100)
camera.position.z = 1500

scene = three.Scene()
scene.fogNode = three.nodes.FogRangeNode(color(0x0000ff), float(1500), float(2100))

amount = 100
radius = 500

textureLoader = TextureLoader(Path(__file__).parent)

map = textureLoader.load('textures/sprite1.png')

group = three.Group()

textureNode = texture(map)

material = three.nodes.SpriteNodeMaterial()
material.colorNode = mul(textureNode, mul(uv(), 2))
material.opacityNode = textureNode.a
material.rotationNode = userData('rotation', 'float')
# get value of: sprite.userData.rotation
material.transparent = True

for a in range(amount):
    x = random() - 0.5
    y = random() - 0.5
    z = random() - 0.5

    sprite = three.Sprite(material)

    sprite.position.set(x, y, z)
    sprite.position.normalize()
    sprite.position.multiplyScalar(radius)

    # individual rotation per sprite
    sprite.userData.rotation = 0

    group.add(sprite)

scene.add(group)
control = three.OrbitControls(camera, canvas)

def loop():
    t = time.time()
    l = len(group.children)
    for i, sprite in enumerate(group.children):
        # material = sprite.material
        scale = math.sin(t + sprite.position.x * 0.01) * 0.3 + 1.0

        imageWidth = 1
        imageHeight = 1

        if map and map.image and map.image.width:
            imageWidth = map.image.width
            imageHeight = map.image.height

        sprite.userData.rotation += 0.1 * (i / l)
        sprite.scale.set(scale * imageWidth, scale * imageHeight, 1.0)

    group.rotation.x = t * 0.5
    group.rotation.y = t * 0.75
    group.rotation.z = t * 1.0

    render.render(scene, camera)


render.setAnimationLoop(loop)


if __name__ == '__main__':
    run()
