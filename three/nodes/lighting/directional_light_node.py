from .analytic_light_node import AnalyticLightNode
from .lights_node import LightsNode
# from ..accessors.object3d_node import Object3DNode
from ..shadernode.shader_node_base_elements import normalize
from ..shadernode.shader_node_elements import uniform
from ..functions.light.getDirectionVector import getDirectionVector

from ...lights import DirectionalLight
from ...math import Vector3


class DirectionalLightNode(AnalyticLightNode):

    def __init__(self, light=None) -> None:
        super().__init__(light)

        self.directionNode = uniform( Vector3() )


    def update(self, frame):
        getDirectionVector( self.light, frame.camera, self.directionNode.value )
        super().update(frame)


    def construct(self, builder):
        # lightPositionViewNode = Object3DNode(Object3DNode.VIEW_POSITION, self.light)
        # targetPositionViewNode = Object3DNode(Object3DNode.VIEW_POSITION, self.light.target)

        # lightDirection = normalize(
        #     sub(lightPositionViewNode, targetPositionViewNode))

        lightDirection = normalize(self.directionNode)

        lightColor = self.colorNode

        lightingModelFunctionNode = builder.context.lightingModelNode
        reflectedLight = builder.context.reflectedLight

        if lightingModelFunctionNode and lightingModelFunctionNode.direct:
            lightingModelFunctionNode.direct.call({
                "lightDirection": lightDirection,
                "lightColor": lightColor,
                "reflectedLight": reflectedLight
            }, builder)


LightsNode.setReference( DirectionalLight, DirectionalLightNode )