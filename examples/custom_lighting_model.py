import three
import three.nodes
from three.nodes import *
import time
import math
from wgpu.gui.auto import WgpuCanvas, run
from pymeshio.pmx import reader
from pathlib import Path


p = Path(__file__).parent / "models" / "miku_pmx" / "blue.pmx"

pmd_file = reader.read_from_file(p)

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

canvas = WgpuCanvas(size=(640, 480),  max_fps=60, title="Phong Light Model")
render = three.WgpuRenderer(canvas,  antialias = True)
#render.outputEncoding = three.sRGBEncoding

render.init()

camera = three.PerspectiveCamera(70, 640 / 480, 0.01, 100)
camera.position.z = 20
camera.position.y = 10

scene = three.Scene()

material = three.MeshBasicMaterial(color = 0xffffff, shinniness = 32.0)

material.side = three.DoubleSide

mesh = three.Mesh(geometry, material)
mesh.rotation.y = math.pi/6 * 5
scene.add(mesh)


sp = three.SphereGeometry(0.5, 16, 8)

light1 = three.PointLight(0xffaa00)
light1.add(three.Mesh(sp, three.MeshBasicMaterial({'color': 0xffaa00})))
scene.add(light1)

light2 = three.PointLight(0x0040ff)
light2.add(three.Mesh(sp, three.MeshBasicMaterial({'color': 0x0040ff})))
scene.add(light2)

light3 = three.PointLight(0x80ff80)
light3.add(three.Mesh(sp, three.MeshBasicMaterial({'color': 0x80ff80})))
scene.add(light3)

allLightsNode = three.nodes.LightsNode().fromLights([light1, light2, light3])


def _phong_light_model(inputs, *args):
    '''
        Reference: https://sotrh.github.io/learn-wgpu/intermediate/tutorial10-lighting/#the-blinn-phong-model
    '''

    lightDirection = inputs['lightDirection']
    lightColor = inputs['lightColor']

    lightColor = lightColor * math.pi

    # ambient
    ambientStrength = 0.1
    ambientColor = lightColor * ambientStrength

    # flat shading
    # normal = add(
    #     mul(normalize(cross(dFdx(positionWorld), dFdy(positionWorld))), 0.5), 0.5)

    # diffuse
    diffuseStrength = max(dot(transformedNormalView, lightDirection), 0)
    diffuseColor = lightColor * diffuseStrength

    halfDirection = normalize(positionViewDirection + lightDirection)
    specularStrength = pow(
        max(dot(normalWorld, halfDirection), 0.0), MaterialReferenceNode('shinniness', 'float'))

    specularColor = specularStrength * lightColor

    total = (ambientColor + diffuseColor+ specularColor) * materialColor
    inputs.reflectedLight.directDiffuse.add(total)
    



phongLightModel = three.nodes.ShaderNode(_phong_light_model)
lightingModelContext = three.nodes.ContextNode(
    allLightsNode, {"lightingModelNode": {"direct": phongLightModel}})

material.lightsNode = lightingModelContext

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

if __name__ == '__main__':
    run()
