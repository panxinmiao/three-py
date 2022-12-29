from .analytic_light_node import AnalyticLightNode
from .lights_node import LightsNode
from ..functions.light.getDistanceAttenuation import getDistanceAttenuation
from ..shadernode.shader_node_base_elements import uniform, mul, normalize, length, sub, positionView, objectViewPosition

from ...lights import PointLight


class PointLightNode(AnalyticLightNode):

    def __init__(self, light=None) -> None:
        super().__init__(light)

        self.cutoffDistanceNode = uniform(0)
        self.decayExponentNode = uniform(0)

    def update(self, frame):
        light = self.light
        super().update(frame)
        self.cutoffDistanceNode.value = light.distance
        self.decayExponentNode.value = light.decay


    def construct(self, builder):
        colorNode = self.colorNode
        cutoffDistanceNode = self.cutoffDistanceNode
        decayExponentNode = self.decayExponentNode
        light = self.light

        # lightPositionViewNode = Object3DNode(Object3DNode.VIEW_POSITION, self.light)
        # lVector = sub(lightPositionViewNode, positionView)

        lVector = sub(objectViewPosition(light), positionView)

        lightDirection = normalize(lVector)
        lightDistance = length(lVector)

        lightAttenuation = getDistanceAttenuation.call({
            "lightDistance": lightDistance,
            "cutoffDistance": cutoffDistanceNode,
            "decayExponent": decayExponentNode
        })

        lightColor = mul(colorNode, lightAttenuation)

        lightingModelFunctionNode = builder.context.lightingModelNode
        reflectedLight = builder.context.reflectedLight

        if lightingModelFunctionNode and lightingModelFunctionNode.direct:
            lightingModelFunctionNode.direct.call({
                "lightDirection": lightDirection,
                "lightColor": lightColor,
                "reflectedLight": reflectedLight
            }, builder)


LightsNode.setReference( PointLight, PointLightNode )