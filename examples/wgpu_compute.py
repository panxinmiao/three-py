import three, math
from random import random
from wgpu.gui.auto import WgpuCanvas, run
import three.nodes as nodes
from three.nodes import (ShaderNode, compute,
                    uniform, element, storage, attribute, mul, sin, cos,
                    temp, assign, add, sub, cond, abs, negate, max, min, length, float, vec2, vec3, color,
                    greaterThanEqual, lessThanEqual, instanceIndex)

canvas = WgpuCanvas(size=(640, 640), max_fps=60, title="wgpu_renderer")

render = three.WgpuRenderer(canvas)
render.init()

camera = three.OrthographicCamera(- 1.0, 1.0, 1.0, - 1.0, 0, 1)
camera.position.z = 1

scene = three.Scene()

pointerVector = three.Vector2(- 10.0, - 10.0)  # Out of bounds first
scaleVector = three.Vector2(1, 1)

particleNum = 300000
particleSize = 2
# vec2

particleArray = three.Float32Array(particleNum * particleSize)
velocityArray = three.Float32Array(particleNum * particleSize)

# cpu init
# for i in range(particleNum):
#     r = random() * 0.01 + 0.005
#     degree = random() * 360
#     velocityArray[i * particleSize + 0] = r * math.sin(degree * math.pi / 180) # x
#     velocityArray[i * particleSize + 1] = r * math.cos(degree * math.pi / 180) # y


# create buffers

particleBuffer = three.InstancedBufferAttribute(particleArray, 2)
velocityBuffer = three.InstancedBufferAttribute(velocityArray, 2)

particleBufferNode = storage(particleBuffer, 'vec2', particleNum)
velocityBufferNode = storage(velocityBuffer, 'vec2', particleNum)


# create function


def __fn_node(inputs, builder):
    particle = element(particleBufferNode, instanceIndex)
    velocity = element(velocityBufferNode, instanceIndex)

    pointer = uniform(pointerVector)
    limit = uniform(scaleVector)

    position = temp(add(particle, velocity), 'tempPos')
    # @ TODO: this should work without 'tempPos' property name
    position.build(builder)

    assign(velocity.x, cond(greaterThanEqual(abs(position.x), limit.x),negate(velocity.x), velocity.x)).build(builder)
    assign(velocity.y, cond(greaterThanEqual(abs(position.y), limit.y),negate(velocity.y), velocity.y)).build(builder)

    assign(position, max(negate(limit), min(limit, position))).build(builder)

    pointerSize = 0.1
    distanceFromPointer = length(sub(pointer, position))

    assign(particle, cond(lessThanEqual(distanceFromPointer,pointerSize), vec3(), position)).build(builder)


fnNode = ShaderNode(__fn_node)


#compute
computeNode = compute(fnNode, particleNum)

# gpu init
def _on_init(renderer):
    def __precomputeShaderNode(inputs, builder):
        particleIndex = float( instanceIndex )
        randomAngle = mul( mul( particleIndex, .005 ), math.pi * 2 )
        randomSpeed = add( mul( particleIndex, 1e-8 ), 1e-7 )

        velX = mul( sin( randomAngle ), randomSpeed )
        velY = mul( cos( randomAngle ), randomSpeed )
        velocity = element( velocityBufferNode, instanceIndex )

        assign( velocity.xy, vec2( velX, velY ) ).build( builder )

    precomputeShaderNode = ShaderNode(__precomputeShaderNode)
    renderer.compute( compute( precomputeShaderNode, computeNode.count ) )

computeNode.onInit = _on_init

particleNode = attribute('particle', 'vec2')

pointsGeometry = three.BufferGeometry()
pointsGeometry.setAttribute('position', three.BufferAttribute(three.Float32Array(3), 3)) # single vertex(not triangle)
pointsGeometry.setAttribute('particle', particleBuffer) # dummy the position points as instances
pointsGeometry.drawRange.count = 1
# force render points as instances(not triangle)

pointsMaterial = nodes.PointsNodeMaterial()
pointsMaterial.colorNode = add(particleNode, color(0xffffff))
pointsMaterial.positionNode = particleNode

mesh = three.Points(pointsGeometry, pointsMaterial)
mesh.isInstancedMesh = True
mesh.count = particleNum
scene.add(mesh)

def on_resize(event):
    camera.updateProjectionMatrix()

canvas.add_event_handler(on_resize, 'resize')

def on_mouse_move(event):
    x = event['x']
    y = event['y']

    width, height = canvas.get_physical_size()
    pointerVector.set(
        (x / width - 0.5) * 2.0,
        (- y / height + 0.5) * 2.0
    )


canvas.add_event_handler(on_mouse_move, 'pointer_move')


def loop():
    render.compute(computeNode)
    render.render(scene, camera)


render.setAnimationLoop(loop)

if __name__ == '__main__':
    run()
