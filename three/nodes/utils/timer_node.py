# from three.renderer.nodes import NodeUpdateType, FloatNode

from ..core.constants import NodeUpdateType
from ..core.uniform_node import UniformNode

class TimerNode(UniformNode):
    LOCAL = 'local'
    GLOBAL = 'global'
    DELTA = 'delta'

    def __init__(self, scope = LOCAL, scale = 1, value = 0) -> None:
        super().__init__(value)

        self.scope = scope
        self.scale = scale
        self.updateType = NodeUpdateType.Frame

    def update( self, frame ):
        scope = self.scope
        scale = self.scale
        
        if scope == TimerNode.LOCAL:
            self.value += frame.deltaTime * scale

        elif scope == TimerNode.DELTA:
            self.value = frame.deltaTime * scale

        else:
            # global
            self.value = frame.time * scale
