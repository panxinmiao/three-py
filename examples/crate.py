import three
from pathlib import Path
from wgpu.gui.auto import WgpuCanvas, run

from loaders.texture_loader import TextureLoader

canvas = WgpuCanvas(size=(640, 480), max_fps=60, title="wgpu_renderer")

render = three.WgpuRenderer(canvas, antialias = True)
render.init()

camera = three.PerspectiveCamera(70, 640 / 480, 0.01, 1000)
camera.position.z = 50

scene = three.Scene()

geometry = three.BoxGeometry(10, 10, 10)

loader = TextureLoader(Path(__file__).parent / "textures" )

texture = loader.load("crate.gif")

material = three.MeshBasicMaterial()
material.map = texture

mesh = three.Mesh(geometry, material)

control = three.OrbitControls(camera, canvas)

scene.add(mesh)

def loop():
    mesh.rotation.x += 0.01
    mesh.rotation.y += 0.02
    render.render(scene, camera)


render.setAnimationLoop(loop)

if __name__ == '__main__':
    run()
