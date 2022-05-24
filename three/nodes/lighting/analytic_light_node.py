from .lighting_node import LightingNode
from ..core.constants import NodeUpdateType
from ..shadernode.shader_node_base_elements import uniform

from three import Color

class AnalyticLightNode(LightingNode):

    def __init__(self, light=None) -> None:
        super().__init__()
        self.updateType = NodeUpdateType.Object
        self.light = light
        self.colorNode = uniform( Color())

    def getHash(self, *args):
        return self.light.uuid

    def update(self, *args):
        self.colorNode.value.copy(self.light.color).multiplyScalar(self.light.intensity)

