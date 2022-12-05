from three.structure import NoneAttribute
from .node_var import NodeVar

class NodeVarying(NodeVar):
    
    isNodeVarying = True

    def __init__(self, name, type) -> None:
        super().__init__(name, type)
        self.needsInterpolation = False