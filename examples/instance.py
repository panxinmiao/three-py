import time, math
import three
from wgpu.gui.auto import WgpuCanvas, run

canvas = WgpuCanvas(size=(640, 480), max_fps = 60, title="wgpu_renderer")

render = three.WgpuRenderer(canvas, antialias = True)
render.init()

camera = three.PerspectiveCamera(70, 640 / 480, 0.01, 100)
camera.position.z = 5

scene = three.Scene()

geometry = three.BoxGeometry(0.2, 0.2, 0.2)
material = three.MeshNormalMaterial()

dummy = three.Object3D()

amount = 8

mesh = three.InstancedMesh(geometry, material, amount*amount*amount)

controls = three.OrbitControls(camera, canvas)

scene.add(mesh)

def loop():

    mesh.rotation.x += 0.01
    mesh.rotation.y += 0.02

    now = time.perf_counter()
    offset = (amount - 1) / 2
    i = 0

    for x in range(amount):
        for y in range(amount):
            for z in range(amount):
                dummy.position.set( 0.3*(offset - x), 0.3*(offset - y), 0.3*(offset - z))
                dummy.rotation.y = (math.sin(x / 4 + now) +
                                    math.sin(y / 4 + now) + 
                                    math.sin(z / 4 + now))
                dummy.rotation.z = dummy.rotation.y * 2
                dummy.updateMatrix()
                mesh.setMatrixAt(i, dummy.matrix)
                i+=1


    render.render(scene, camera)

render.setAnimationLoop(loop)

if __name__ == '__main__':
    run()


