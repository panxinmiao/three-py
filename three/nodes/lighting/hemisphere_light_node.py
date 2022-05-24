from .analytic_light_node import AnalyticLightNode
from .lights_node import LightsNode
from ..accessors.object3d_node import Object3DNode
from ..shadernode.shader_node_base_elements import uniform, add, mul, dot, mix, normalize, normalView

from three import Color

class HemisphereLightNode(AnalyticLightNode):

    def __init__(self, light=None) -> None:
        super().__init__(light)

        self.lightPositionNode = Object3DNode(Object3DNode.POSITION)
        self.lightDirectionNode = normalize(self.lightPositionNode)

        self.groundColorNode = uniform( Color())

    def update(self, frame):

        super().update(frame)

        self.lightPositionNode.object3d = self.light

        self.groundColorNode.value.copy(self.light.groundColor).multiplyScalar(self.light.intensity)

    def generate(self, builder):
        colorNode = self.colorNode
        groundColorNode = self.groundColorNode
        lightDirectionNode = self.lightDirectionNode

        dotNL = dot(normalView, lightDirectionNode)
        hemiDiffuseWeight = add(mul(0.5, dotNL), 0.5)

        irradiance = mix(groundColorNode, colorNode, hemiDiffuseWeight)

        builder.context.irradiance.add(irradiance)

# LightsNode.setReference( HemisphereLight, HemisphereLightNode )