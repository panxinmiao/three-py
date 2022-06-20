import imageio
import three
from pathlib import Path
from wgpu.gui.auto import WgpuCanvas, run

from utils.fps_recorder import FPSRecorder

canvas = WgpuCanvas(size=(640, 480), max_fps=60, title="wgpu_renderer")

render = three.WgpuRenderer(canvas, antialias = True)
render.init()

camera = three.PerspectiveCamera(70, 640 / 480, 0.01, 1000)
camera.position.z = 50

scene = three.Scene()

geometry = three.BoxGeometry(10, 10, 10)

data = imageio.imread(Path(__file__).parent / "textures" / "crate.gif")

image = three.Image(memoryview(data), width=data.shape[1], height=data.shape[0])

tex = three.Texture(image)
tex.needsUpdate = True

material = three.MeshBasicMaterial()
material.map = tex

group = three.Group()

for x in range(5):
    for y in range(5):
        for z in range(5):
            mesh = three.Mesh(geometry, material)
            mesh.position.set(x * 10, y * 10, z * 10)
            group.add(mesh)

scene.add(group)

control = three.OrbitControls(camera, canvas)

def loop():
    group.rotation.x += 0.01
    group.rotation.y += 0.02
    render.render(scene, camera)



render.setAnimationLoop(loop)

if __name__ == '__main__':
    run()
