from .node_material import NodeMaterial
from three.materials import SpriteMaterial

from ..shadernode.shader_node_elements import (
    vec2, vec3, vec4,
    uniform, add, mul, sub,
    positionLocal, length, cos, sin,
    modelViewMatrix, cameraProjectionMatrix, modelWorldMatrix, materialRotation
)

defaultValues = SpriteMaterial()

class SpriteNodeMaterial(NodeMaterial):

    isSpriteNodeMaterial = True

    def __init__(self, parameters=None) -> None:
        super().__init__()

        self.lights = False
        self.normals = False

        self.colorNode = None
        self.opacityNode = None

        self.alphaTestNode = None

        self.lightNode = None

        self.positionNode = None
        self.rotationNode = None
        self.scaleNode = None

        self.setDefaultValues(defaultValues)

        self.setValues(parameters)

    def constructPosition( self, builder, stack ):
        positionNode = self.positionNode
        vertex = positionLocal

        mvPosition = mul(modelViewMatrix, vec4(positionNode.xyz, 1) if positionNode else vec4(0, 0, 0, 1))

        scale = vec2(
            length(vec3(modelWorldMatrix[0].x, modelWorldMatrix[0].y, modelWorldMatrix[0].z)),
            length(vec3(modelWorldMatrix[1].x, modelWorldMatrix[1].y, modelWorldMatrix[1].z))
        )

        if self.scaleNode:
            scale = mul(scale, self.scaleNode)

        alignedPosition = vertex.xy

        if builder.object.center and builder.object.center.isVector2:
            alignedPosition = sub(alignedPosition, sub(uniform(builder.object.center), vec2(0.5)))

        alignedPosition = mul(alignedPosition, scale)

        rotation = self.rotationNode or materialRotation

        rotatedPosition = vec2(
            sub(mul(cos(rotation), alignedPosition.x),
                mul(sin(rotation), alignedPosition.y)),
            add(mul(sin(rotation), alignedPosition.x),
                mul(cos(rotation), alignedPosition.y))
        )

        mvPosition = vec4(add(mvPosition.xy, rotatedPosition.xy), mvPosition.z, mvPosition.w)

        modelViewProjection = mul(cameraProjectionMatrix, mvPosition)

        builder.context.vertex = vertex

        return modelViewProjection

    def copy(self, source):

        self.colorNode = source.colorNode
        self.opacityNode = source.opacityNode

        self.alphaTestNode = source.alphaTestNode

        self.lightNode = source.lightNode

        self.positionNode = source.positionNode
        self.rotationNode = source.rotationNode
        self.scaleNode = source.scaleNode

        return super().copy(source)
