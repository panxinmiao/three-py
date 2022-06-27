
from .buffer_node import BufferNode

class StorageBufferNode(BufferNode):

    isStorageBufferNode = True

    def __init__(self, value, bufferType, bufferCount=0):
        super().__init__(value, bufferType, bufferCount)
        

    def getInputType(self, *args):
        return 'storageBuffer'

    