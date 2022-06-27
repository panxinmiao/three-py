from .buffer_attribute import BufferAttribute
from ..structure import TypedArray

class InstancedBufferAttribute(BufferAttribute):

    isInstancedBufferAttribute = True

    def __init__(self, ary: TypedArray, itemSize, normalized=False, meshPerAttribute=1 ) -> None:
        super().__init__(ary, itemSize, normalized)

        self.meshPerAttribute = meshPerAttribute

    def copy(self, source: 'InstancedBufferAttribute'):
        super().copy(source)

        self.meshPerAttribute = source.meshPerAttribute
        return self
