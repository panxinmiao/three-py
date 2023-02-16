import math, time
import random
import three
import three.nodes
from three.nodes import ShaderNode, vec3, dot, triplanarTexture, viewportBottomLeft
from pathlib import Path
from wgpu.gui.auto import WgpuCanvas, run

from loaders.texture_loader import TextureLoader
from pathlib import Path

canvas = WgpuCanvas(size=(640, 480), title="materials")
renderer = three.WgpuRenderer(canvas, antialias=True)
renderer.init()

camera = three.PerspectiveCamera(45, 640 / 480, 0.1, 2500)
camera.position.set(0, 200, 800)
scene = three.Scene()


# Grid

helper = three.GridHelper( 1000, 40, 0x303030, 0x303030 )
helper.position.y = - 75
scene.add( helper )

# Materials
materials = []

loader = TextureLoader(Path(__file__).parent / "textures" )

texture = loader.load("uv_grid.jpg")
texture.wrapS = three.RepeatWrapping
texture.wrapT = three.RepeatWrapping

opacityTexture = loader.load('alphaMap.jpg')
opacityTexture.wrapS = three.RepeatWrapping
opacityTexture.wrapT = three.RepeatWrapping


# BASIC

# PositionNode.LOCAL
material = three.nodes.MeshBasicNodeMaterial()
material.colorNode = three.nodes.PositionNode( three.nodes.PositionNode.LOCAL )
materials.append( material )

# NormalNode.LOCAL
material = three.nodes.MeshBasicNodeMaterial()
material.colorNode = three.nodes.NormalNode( three.nodes.NormalNode.LOCAL )
materials.append( material )

# NormalNode.WORLD
material = three.nodes.MeshBasicNodeMaterial()
material.colorNode = three.nodes.NormalNode( three.nodes.NormalNode.WORLD )
materials.append( material )

# NormalNode.VIEW
material = three.nodes.MeshBasicNodeMaterial()
material.colorNode = three.nodes.NormalNode( three.nodes.NormalNode.VIEW )
materials.append( material )

# TextureNode
material = three.nodes.MeshBasicNodeMaterial()
material.colorNode = three.nodes.TextureNode( texture )
materials.append( material )

# Opacity
material = three.nodes.MeshBasicNodeMaterial()
material.colorNode = three.nodes.UniformNode( three.Color( 0x0099FF ) )
material.opacityNode = three.nodes.TextureNode( texture )
material.transparent = True
materials.append( material )

# AlphaTest
material = three.nodes.MeshBasicNodeMaterial()
material.colorNode = three.nodes.TextureNode( texture )
material.opacityNode = three.nodes.TextureNode( opacityTexture )
material.alphaTestNode = three.nodes.UniformNode( 0.5 )
materials.append( material )

# Normal
material = three.nodes.MeshNormalNodeMaterial()
material.opacity = 0.5
material.transparent = True
materials.append( material )


# ADVANCED

# Custom ShaderNode ( desaturate filter )

desaturateShaderNode = ShaderNode( lambda color: dot( vec3( 0.299, 0.587, 0.114 ), color.xyz ))

material = three.nodes.MeshBasicNodeMaterial()
material.colorNode = desaturateShaderNode( color = three.nodes.TextureNode( texture ) )
materials.append( material )

# Custom ShaderNode(no inputs) > Approach 2

desaturateNoInputsShaderNode = ShaderNode( lambda: dot( vec3( 0.299, 0.587, 0.114 ), three.nodes.texture( texture ).xyz ))
material = three.nodes.MeshBasicNodeMaterial()
material.colorNode = desaturateNoInputsShaderNode
materials.append( material )

# Custom WGSL ( desaturate filter )

desaturateWGSLNode = three.nodes.FunctionNode('''
    fn desaturate( color:vec3<f32> ) -> vec3<f32> {
        let lum = vec3<f32>( 0.299, 0.587, 0.114 );
        return vec3<f32>( dot( lum, color ) );
    }
''')

material = three.nodes.MeshBasicNodeMaterial()
material.colorNode = desaturateWGSLNode( { 'color': three.nodes.TextureNode( texture ) } )
materials.append( material )

# Custom WGSL ( get texture from keywords )

getWGSLTextureSample = three.nodes.FunctionNode('''
    fn getWGSLTextureSample( tex: texture_2d<f32>, tex_sampler: sampler, uv:vec2<f32> ) -> vec4<f32> {
        return textureSample( tex, tex_sampler, uv ) * vec4<f32>( 0.0, 1.0, 0.0, 1.0 );
    }
''')

textureNode = three.nodes.TextureNode( texture )
# getWGSLTextureSample.keywords = { 'tex': textureNode, 'tex_sampler': sampler( textureNode ) }
material = three.nodes.MeshBasicNodeMaterial()
material.colorNode = getWGSLTextureSample( { 'tex': textureNode, 'tex_sampler': textureNode, 'uv': three.nodes.UVNode() } )
materials.append( material )

# Triplanar Texture Mapping
material = three.nodes.MeshBasicNodeMaterial()
material.colorNode = triplanarTexture( three.nodes.TextureNode( texture ) )
materials.append( material )

# Screen Projection Texture
material = three.nodes.MeshBasicNodeMaterial()
material.colorNode = three.nodes.texture( texture, viewportBottomLeft )
materials.append( material )

# Geometry
objects = []

geometry = three.TeapotGeometry( 50, 18 )

def addMesh( geometry, material ):
    mesh = three.Mesh( geometry, material )
    mesh.position.x = ( len(objects) % 4 ) * 200 - 300
    mesh.position.z = math.floor( len(objects) / 4 ) * 200 - 200
    mesh.rotation.x = random.random() * 200 - 100
    mesh.rotation.y = random.random() * 200 - 100
    mesh.rotation.z = random.random() * 200 - 100
    objects.append( mesh )
    scene.add( mesh )

for material in materials:
    addMesh( geometry, material )


# three.OrbitControls(camera, canvas)

def on_resize(event):
    camera.aspect = event['width'] / event['height']
    camera.updateProjectionMatrix()

canvas.add_event_handler(on_resize, 'resize')

def animate():
    timer = time.time() * 0.1
    camera.position.x = math.cos( timer ) * 1000
    camera.position.z = math.sin( timer ) * 1000
    camera.lookAt( scene.position )

    for obj in objects:
        obj.rotation.x += 0.01
        obj.rotation.y += 0.005

    renderer.render(scene, camera)

renderer.setAnimationLoop(animate)

if __name__ == "__main__":
    run()