import imageio
import three
from pathlib import Path
from wgpu.gui.auto import WgpuCanvas, run

canvas = WgpuCanvas(size=(640, 480), max_fps=60, title="wgpu_renderer")

render = three.WgpuRenderer(canvas, parameters={'antialias': True})
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

mesh = three.Mesh(geometry, material)

control = three.OrbitControls(camera, canvas)

scene.add(mesh)

def loop():
    mesh.rotation.x += 0.01
    mesh.rotation.y += 0.02
    render.render(scene, camera)


render.setAnimationLoop(loop)

run()
