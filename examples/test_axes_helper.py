import three
from wgpu.gui.auto import WgpuCanvas, run

canvas = WgpuCanvas(size=(640, 480), title="wgpu_renderer")

render = three.WgpuRenderer(canvas, parameters={'antialias': True})
render.init()

camera = three.PerspectiveCamera(70, 640 / 480, 0.01, 100)
camera.position.set(0.5, 0.5, 1)

scene = three.Scene()

geometry = three.BoxGeometry(0.2, 0.2, 0.2)
material = three.MeshNormalMaterial()

mesh = three.Mesh(geometry, material)
scene.add(mesh)

axes = three.AxesHelper(0.5)
scene.add(axes)

controls = three.OrbitControls(camera, canvas)

def loop():
    render.render(scene, camera)

render.setAnimationLoop(loop)

run()