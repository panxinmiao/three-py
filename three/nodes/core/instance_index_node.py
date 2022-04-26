from .node import Node

class InstanceIndexNode(Node):

    def __init__(self) -> None:
        super().__init__('uint')

    def generate(self, builder):
        return builder.getInstanceIndex()
