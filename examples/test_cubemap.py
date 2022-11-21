import three
import three.nodes
import imageio
import numpy as np
from pathlib import Path
from wgpu.gui.auto import WgpuCanvas, run

from loaders.texture_loader import TextureLoader, CubeTextureLoader


canvas = WgpuCanvas(size=(640, 640), max_fps=60, title="wgpu_renderer")

render = three.WgpuRenderer(canvas, antialias=True)
render.init()

camera = three.PerspectiveCamera(90, 1, 0.1, 10000)
scene = three.Scene()


cubemap_path = Path(__file__).parent / "textures" / "cube" / "cubemap.jpg"


data = imageio.imread(Path(cubemap_path), pilmode='RGBA')

h = data.shape[0]//3
w = data.shape[1]//4

posx_d = np.ascontiguousarray(data[1*h:2*h, 2*w:3*w])
posx = three.Image(memoryview(posx_d), w, h)

negx_d = np.ascontiguousarray(data[1*h:2*h, 0*w:1*w])
negx = three.Image(memoryview(negx_d), w, h)

posy_d = np.ascontiguousarray(data[0*h:1*h, 1*w:2*w])
posy = three.Image(memoryview(posy_d), w, h)

negy_d = np.ascontiguousarray(data[2*h:3*h, 1*w:2*w])
negy = three.Image(memoryview(negy_d), w, h)

posz_d = np.ascontiguousarray(data[1*h:2*h, 1*w:2*w])
posz = three.Image(memoryview(posz_d), w, h)

negz_d = np.ascontiguousarray(data[1*h:2*h, 3*w:4*w])
negz = three.Image(memoryview(negz_d), w, h)

text = three.Texture(posy)
text.needsUpdate = True

cubeTexture = three.CubeTexture([posx, negx, posy, negy, posz, negz])
# cubeTexture.type = three.UnsignedByteType
cubeTexture.needsUpdate = True

cubeTexture.encoding = three.sRGBEncoding

# scene.add(three.AmbientLight(0x111111))
material = three.MeshStandardMaterial()

material.roughness = 0.05
material.metalness = 1
material.envMap = cubeTexture

# geometry = three.BoxGeometry(1, 1, 1)
geometry = three.SphereGeometry(2, 32, 32)
mesh = three.Mesh(geometry, material)
scene.add(mesh)



scene.background = cubeTexture

# scene.environmentNode = scene.background

render.outputEncoding = three.sRGBEncoding

camera.position.z = 5
# camera.up.set(0, 0, 1)
# camera.lookAt(0, -1, 0)

three.OrbitControls(camera, canvas)

def on_resize(event):
    camera.aspect = event['width'] / event['height']
    camera.updateProjectionMatrix()

canvas.add_event_handler(on_resize, 'resize')

def loop():

    render.render(scene, camera)

render.setAnimationLoop(loop)


if __name__ == "__main__":
    run()
