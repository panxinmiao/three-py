from ..core.node import Node

class FrontFacingNode(Node):

    def __init__(self) -> None:
        super().__init__('bool')

    def generate(self, builder):
        return builder.getFrontFacing()

    
