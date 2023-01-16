from ..core.uniform_node import UniformNode

class BufferNode(UniformNode):

    isBufferNode = True

    def __init__(self, value, bufferType, bufferCount = 0) -> None:
        super().__init__(value, bufferType )
        self.bufferType = bufferType
        self.bufferCount = bufferCount

    def getInputType(self, *args): # /*builder*/
        return 'buffer'