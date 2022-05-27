import three
from wgpu.gui.auto import WgpuCanvas, run

canvas = WgpuCanvas(size=(640, 480), max_fps=60, title="wgpu_renderer")

render = three.WgpuRenderer(canvas, parameters={'antialias': True})
render.init()

camera = three.PerspectiveCamera(70, 640 / 480, 0.01, 100)
camera.position.z = 1

scene = three.Scene()

geometry = three.BoxGeometry(0.2, 0.2, 0.2)
material = three.MeshNormalMaterial()

mesh = three.Mesh(geometry, material)

scene.add(mesh)

def loop():
    mesh.rotation.x += 0.01
    mesh.rotation.y += 0.02
    render.render(scene, camera)

render.setAnimationLoop(loop)

run()


