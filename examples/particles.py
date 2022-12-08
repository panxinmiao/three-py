import three
from wgpu.gui.auto import WgpuCanvas, run
import three.nodes
from three.nodes import  range, texture, mix, uv, mul, mod, rotateUV, color, max, min, div, clamp, positionWorld, invert, timerLocal
# from three.nodes import range as rangeNode
from loaders.texture_loader import TextureLoader
from pathlib import Path

canvas = WgpuCanvas(size=(640, 480), max_fps = 60, title="wgpu_renderer")

render = three.WgpuRenderer(canvas, antialias = True)
render.init()

camera = three.PerspectiveCamera(60, 640 / 480, 1, 5000)
camera.position.set( 1300, 500, 0 )

scene = three.Scene()

# textures
loader = TextureLoader(Path(__file__).parent / "textures" )
map = loader.load("smoke.png")

# create nodes
lifeRange = range( .1, 1 )
offsetRange = range(three.Vector3( - 2, 3, - 2 ), three.Vector3( 2, 5, 2 ) )

timer = timerLocal( .2, 1 )

lifeTime = mod( mul( timer, lifeRange ), 1 )
scaleRange = range( .3, 2 )
rotateRange = range( .1, 4 )

life = div( lifeTime, lifeRange )
fakeLightEffect = max( .2, invert( positionWorld.y ) )
textureNode = texture( map, rotateUV( uv(), mul( timer, rotateRange ) ) )
opacityNode = mul( textureNode.a, invert( life ) )
smokeColor = mix( color( 0x2c1501 ), color( 0x222222 ), clamp( mul( positionWorld.y, 3 ) ) )

# create particles

smokeNodeMaterial = three.nodes.SpriteNodeMaterial()
smokeNodeMaterial.colorNode = mul( mix( color( 0xf27d0c ), smokeColor, min( mul( life, 2.5 ), 1 ) ), fakeLightEffect )
smokeNodeMaterial.opacityNode = opacityNode
smokeNodeMaterial.positionNode = mul( offsetRange, lifeTime )
smokeNodeMaterial.scaleNode = mul( scaleRange, max( .3, lifeTime ) )
smokeNodeMaterial.depthWrite = False
smokeNodeMaterial.transparent = True

#smokeInstancedSprite = three.Sprite( smokeNodeMaterial )
smokeInstancedSprite = three.Mesh( three.PlaneGeometry(1, 1), smokeNodeMaterial )
smokeInstancedSprite.scale.setScalar( 400 )
smokeInstancedSprite.isInstancedMesh = True
smokeInstancedSprite.count = 2000
scene.add( smokeInstancedSprite )

#

fireNodeMaterial = three.nodes.SpriteNodeMaterial()
fireNodeMaterial.colorNode = mix( color( 0xb72f17 ), color( 0xb72f17 ), life )
fireNodeMaterial.positionNode = mul( range( three.Vector3( -1, 1, -1 ), three.Vector3( 1, 2, 1 ) ), lifeTime )
fireNodeMaterial.scaleNode = smokeNodeMaterial.scaleNode
fireNodeMaterial.opacityNode = opacityNode
fireNodeMaterial.blending = three.AdditiveBlending
fireNodeMaterial.transparent = True
fireNodeMaterial.depthWrite = False

# fireInstancedSprite = three.Sprite( fireNodeMaterial )
fireInstancedSprite = three.Mesh( three.PlaneGeometry(1, 1), fireNodeMaterial )
fireInstancedSprite.scale.setScalar( 400 )
fireInstancedSprite.isInstancedMesh = True
fireInstancedSprite.count = 100
fireInstancedSprite.position.y = - 100
fireInstancedSprite.renderOrder = 1
scene.add( fireInstancedSprite )

# todo: helpers

# 
controls = three.OrbitControls( camera, canvas )
controls.maxDistance = 2700
controls.target.set( 0, 500, 0 )
controls.update()

def on_resize(event):
    camera.aspect = event['width'] / event['height']
    camera.updateProjectionMatrix()

canvas.add_event_handler(on_resize, 'resize')

def loop():
    render.render(scene, camera)

render.setAnimationLoop(loop)

if __name__ == '__main__':
    run()


