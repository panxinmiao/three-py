from .node import Node

class InstanceIndexNode(Node):

    isInstanceIndexNode = True

    def __init__(self) -> None:
        super().__init__('uint')

    def generate(self, builder):
        return builder.getInstanceIndex()
