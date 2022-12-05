from ..core.node import Node
from ..shadernode.shader_node_base_elements import uniform, div, vec2, invert
from three import Vector2
from ..core.constants import NodeUpdateType

class ViewportNode(Node):
    _resolution = None

    isScreenNode = True

    COORDINATE = 'coordinate'
    RESOLUTION = 'resolution'
    TOP_LEFT = 'topLeft'
    BOTTOM_LEFT = 'bottomLeft'
    TOP_RIGHT = 'topRight'
    BOTTOM_RIGHT = 'bottomRight'

    def __init__(self, scope) -> None:
        super().__init__()
        self.scope = scope

    def getNodeType(self, *args):
        return 'vec4' if self.scope == self.COORDINATE else 'vec2'

    def getUpdateType(self, *args):
        updateType = NodeUpdateType.NONE

        if self.scope == ViewportNode.RESOLUTION:
            updateType = NodeUpdateType.Frame
        
        self.updateType = updateType

        return updateType

    def update(self, frame):
        renderer = frame.renderer
        renderer.getSize(ViewportNode._resolution)
    
    def construct(self, builder):
        scope = self.scope

        if scope == ViewportNode.COORDINATE:
            return
        
        if scope == ViewportNode.RESOLUTION:
            ViewportNode._resolution = ViewportNode._resolution or Vector2()
            output = uniform(ViewportNode._resolution)
        
        else:
            coordinateNode = vec2(ViewportNode(ViewportNode.COORDINATE))
            resolutionNode = ViewportNode(ViewportNode.RESOLUTION)

            output = div(coordinateNode, resolutionNode)

            outX = output.x
            outY = output.y

            if 'top' in scope and builder.isFlipY():
                outY = invert(outY)
            elif 'bottom' in scope and not builder.isFlipY():
                outY = invert(outY)
            if 'right' in scope:
                outX = invert(outX)
            
            output = vec2(outX, outY)
        
        return output
    
    def generate(self, builder):

        if self.scope == ViewportNode.COORDINATE:
            return builder.getFragCoord()
        
        return super().generate(builder)