from .analytic_light_node import AnalyticLightNode
from .lights_node import LightsNode

from ...lights import AmbientLight

class AmbientLightNode(AnalyticLightNode):

    def __init__(self, light=None) -> None:
        super().__init__(light)

    def construct(self, builder):
        colorNode = self.colorNode
        builder.context.irradiance.add( colorNode )

LightsNode.setReference( AmbientLight, AmbientLightNode )