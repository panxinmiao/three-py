import math
import three
from wgpu.gui.auto import WgpuCanvas, run
from pathlib import Path
from loaders.texture_loader import TextureLoader

canvas = WgpuCanvas(size=(600, 400), max_fps=60, title="Geometries")

render = three.WgpuRenderer(canvas, antialias = True)
render.init()

#camera = three.PerspectiveCamera(70, 640 / 480, 0.01, 200)
camera = three.OrthographicCamera(-75, 75, 50, -50, 0.01, 200)
camera.position.z = 100

scene = three.Scene()

torusGeometry = three.TorusGeometry(10, 3, 16, 100)
torusKnotGeometry = three.TorusKnotGeometry(10, 3, 100, 16)
coneGeometry = three.ConeGeometry( 10, 30, 32 )

points = []
for i in range(10):
    points.append( three.Vector2( math.sin( i * 0.2 ) * 10 + 5, ( i - 5 ) * 2 ) )

latheGeometry = three.LatheGeometry( points )
cylinderGeometry = three.CylinderGeometry( 5, 5, 20, 32 )

sphereGeometry = three.SphereGeometry( 10, 32, 16 )

# material = three.MeshStandardMaterial(side = three.DoubleSide, color = 0x049ef4)
# material.flatShading = True

loader = TextureLoader(Path(__file__).parent / "textures" )

texture = loader.load("uv_grid.jpg")

material = three.MeshBasicMaterial(side = three.DoubleSide)
material.map = texture

torusMesh = three.Mesh(torusGeometry, material)
torusMesh.position.x = -40
torusMesh.position.y = 20

torusKnotMesh = three.Mesh(torusKnotGeometry, material)
torusKnotMesh.position.x = 0
torusKnotMesh.position.y = 20

coneMesh = three.Mesh(coneGeometry, material)
coneMesh.position.x = 40
coneMesh.position.y = 20

latheMesh = three.Mesh(latheGeometry, material)
latheMesh.position.x = -40
latheMesh.position.y = -20

cylinderMesh = three.Mesh(cylinderGeometry, material)
cylinderMesh.position.x = 0
cylinderMesh.position.y = -20

sphereMesh = three.Mesh(sphereGeometry, material)
sphereMesh.position.x = 40
sphereMesh.position.y = -20

scene.add(torusMesh)
scene.add(torusKnotMesh)
scene.add(coneMesh)
scene.add(latheMesh)
scene.add(cylinderMesh)
scene.add(sphereMesh)

# light1 = three.DirectionalLight( 0xffffff, 2 )
# scene.add( light1 )

# light2 = three.AmbientLight( 0xeeeeee, 2 )
# scene.add( light2 )

control = three.OrbitControls(camera, canvas)

def loop():
    torusMesh.rotation.x += 0.01
    torusMesh.rotation.y += 0.02

    torusKnotMesh.rotation.x += 0.01
    torusKnotMesh.rotation.y += 0.02

    coneMesh.rotation.x += 0.01
    coneMesh.rotation.y += 0.02

    latheMesh.rotation.x += 0.01
    latheMesh.rotation.y += 0.02

    cylinderMesh.rotation.x += 0.01
    cylinderMesh.rotation.y += 0.02

    sphereMesh.rotation.x += 0.01
    sphereMesh.rotation.y += 0.02

    render.render(scene, camera)

render.setAnimationLoop(loop)

if __name__ == '__main__':
    run()
