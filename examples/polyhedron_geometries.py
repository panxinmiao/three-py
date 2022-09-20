import three
from wgpu.gui.auto import WgpuCanvas, run

canvas = WgpuCanvas(size=(640, 640), max_fps=60, title="PolyhedronGeometrys")

render = three.WgpuRenderer(canvas, antialias = True)
render.init()

#camera = three.PerspectiveCamera(70, 640 / 640, 0.01, 200)
camera = three.OrthographicCamera(-20, 20, 20, -20, 0.01, 200)
camera.position.z = 100

scene = three.Scene()

material = three.MeshNormalMaterial(side = three.DoubleSide)
material.flatShading = True

verticesOfCube = [
    -1,-1,-1,    1,-1,-1,    1, 1,-1,    -1, 1,-1,
    -1,-1, 1,    1,-1, 1,    1, 1, 1,    -1, 1, 1,
]
indicesOfFaces = [
    2,1,0,    0,3,2,
    0,4,7,    7,3,0,
    0,1,5,    5,4,0,
    1,2,6,    6,5,1,
    2,3,7,    7,6,2,
    4,5,6,    6,7,4
]

geometry = three.PolyhedronGeometry( verticesOfCube, indicesOfFaces, 6, 2 )
mesh = three.Mesh(geometry, material)
scene.add(mesh)

ico = three.Mesh(three.IcosahedronGeometry( 6 ), material)
ico.position.x = -10
ico.position.y = -10
scene.add(ico)

oct = three.Mesh(three.OctahedronGeometry( 6 ), material)
oct.position.x = 10
oct.position.y = -10
scene.add(oct)

dodeca = three.Mesh(three.DodecahedronGeometry( 6 ), material)
dodeca.position.x = -10
dodeca.position.y = 10
scene.add(dodeca)

tetra = three.Mesh(three.TetrahedronGeometry( 6 ), material)
tetra.position.x = 10
tetra.position.y = 10
scene.add(tetra)

control = three.OrbitControls(camera, canvas)

def loop():
    mesh.rotation.x += 0.01
    mesh.rotation.y += 0.02

    ico.rotation.x += 0.01
    ico.rotation.y += 0.02

    oct.rotation.x += 0.01
    oct.rotation.y += 0.02

    dodeca.rotation.x += 0.01
    dodeca.rotation.y += 0.02

    tetra.rotation.x += 0.01
    tetra.rotation.y += 0.02

    render.render(scene, camera)

render.setAnimationLoop(loop)

if __name__ == '__main__':
    run()
