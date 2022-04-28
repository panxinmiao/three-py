import three
import time
import math
from PyQt5 import QtWidgets
from wgpu.gui.qt import WgpuCanvas
from pymeshio.pmx import reader
app = QtWidgets.QApplication([])

pmd_file = reader.read_from_file(r'examples/miku_pmx/blue.pmx')

positions = []
normals = []
uvs = []

for v in pmd_file.vertices:
    p = v.position
    positions.append(p.x)
    positions.append(p.y)
    positions.append(p.z)

    n = v.normal
    normals.append(n.x)
    normals.append(n.y)
    normals.append(n.z)

    uv = v.uv
    uvs.append(uv.x)
    uvs.append(uv.y)


geometry = three.BufferGeometry()

geometry.setAttribute('position', three.Float32BufferAttribute(positions, 3))
geometry.setAttribute('normal', three.Float32BufferAttribute(normals, 3))
geometry.setAttribute('uv', three.Float32BufferAttribute(uvs, 2))

geometry.setIndex(pmd_file.indices)
# geometry.computeVertexNormals()

canvas = WgpuCanvas(size=(640, 480), title="Physical Light")
render = three.WgpuRenderer(canvas, parameters={'antialias': True})

render.init()

camera = three.PerspectiveCamera(70, 640 / 480, 0.01, 100)
camera.position.z = 20
camera.position.y = 10

scene = three.Scene()

material = three.MeshStandardMaterial({'color': 0x0ffffff})

material.side = three.DoubleSide

mesh = three.Mesh(geometry, material)
mesh.rotation.y = math.pi/6 * 5

scene.add(mesh)

light = three.PointLight(three.Color(0xffffff), 2, 1000)
light.position.set(10, 20, 0)
sp = three.SphereGeometry(0.5, 16, 8)
light.add(three.Mesh(sp, three.MeshBasicMaterial({'color': 0xffffff})))
scene.add(light)

control = three.OrbitControls(camera, canvas)

control.target.y = 10
control.target0.y = 10
control.update()


def on_resize(event):
    camera.aspect = event['width'] / event['height']
    camera.updateProjectionMatrix()


canvas.add_event_handler(on_resize, 'resize')


def loop():
    t = time.time() * 0.5

    light.position.x = math.sin(t) * 10
    light.position.y = math.sin(t) * 5 + 15
    light.position.z = math.cos(t) * 10

    render.render(scene, camera)


render.setAnimationLoop(loop)
app.exec_()
