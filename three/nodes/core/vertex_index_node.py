from .node import Node

class VertexIndexNode(Node):

    isVertexIndexNode = True

    def __init__(self) -> None:
        super().__init__('uint')

    def generate(self, builder):
        return builder.getVertexIndex()