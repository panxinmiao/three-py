import three
import three.nodes
from three.nodes import *
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

canvas = WgpuCanvas(size=(640, 480), title="Phong Light Model")
render = three.WgpuRenderer(canvas, parameters={'antialias': True})

render.init()

camera = three.PerspectiveCamera(70, 640 / 480, 0.01, 100)
camera.position.z = 20
camera.position.y = 10

scene = three.Scene()

material = three.MeshStandardMaterial({'color': 0xffffff})

material.side = three.DoubleSide

mesh = three.Mesh(geometry, material)
mesh.rotation.y = math.pi/6 * 5
scene.add(mesh)


sp = three.SphereGeometry(0.5, 16, 8)

light1 = three.PointLight(0xffaa00, 2)
light1.add(three.Mesh(sp, three.MeshBasicMaterial({'color': 0xffaa00})))
scene.add(light1)

light2 = three.PointLight(0x0040ff, 2)
light2.add(three.Mesh(sp, three.MeshBasicMaterial({'color': 0x0040ff})))
scene.add(light2)

light3 = three.PointLight(0x80ff80, 2)
light3.add(three.Mesh(sp, three.MeshBasicMaterial({'color': 0x80ff80})))
scene.add(light3)

allLightsNode = three.nodes.LightsNode().fromLights([light1, light2, light3])


def _phong_light_model(inputs, *args):
    '''
        Reference: https://sotrh.github.io/learn-wgpu/intermediate/tutorial10-lighting/#the-blinn-phong-model
    '''

    lightDirection = inputs['lightDirection']
    lightColor = inputs['lightColor']

    # ambient
    ambientStrength = 0.1
    ambientColor = mul(lightColor, ambientStrength)

    # flat shading
    # normal = add(
    #     mul(normalize(cross(dFdx(positionWorld), dFdy(positionWorld))), 0.5), 0.5)

    # diffuse
    diffuseStrength = max(dot(transformedNormalView, lightDirection), 0)
    diffuseColor = mul(lightColor, diffuseStrength)

    # specular
    viewDirection = normalize(sub(positionView, positionWorld))
    reflectDirection = reflect(sub(0, lightDirection), normalWorld)
    specularStrength = pow(
        max(dot(viewDirection, reflectDirection), 0.0), 32.0)
    specularColor = mul(specularStrength, lightColor)

    total = mul(add(add(ambientColor, diffuseColor),
                specularColor), materialColor)

    # trick, outlight = directDiffuse + directSpecular + indirectDiffuse + indirectSpecular
    inputs.reflectedLight.directDiffuse.add(total)


phongLightModel = three.nodes.ShaderNode(_phong_light_model)
lightingModelContext = three.nodes.LightContextNode(
    allLightsNode, phongLightModel)
material.lightNode = lightingModelContext


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
    scale = 10

    light1.position.x = math.sin(t) * scale
    light1.position.y = math.sin(t) * 5 + 15
    light1.position.z = math.cos(t) * scale

    light2.position.x = math.sin(t + math.pi * 2/3) * scale
    light2.position.y = math.sin(t + math.pi * 1/3) * 5 + 15
    light2.position.z = math.cos(t + math.pi * 2/3) * scale

    light3.position.x = math.sin(t + math.pi * 4/3) * scale
    light3.position.y = math.sin(t + math.pi * 2/3) * 5 + 15
    light3.position.z = math.cos(t + math.pi * 4/3) * scale

    render.render(scene, camera)


render.setAnimationLoop(loop)

app.exec_()
