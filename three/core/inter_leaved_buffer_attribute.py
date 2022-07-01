
from ..structure import NoneAttribute
from .buffer_attribute import BufferAttribute
from .inter_leaved_buffer import InterleavedBuffer

class InterleavedBufferAttribute(NoneAttribute):

    isInterleavedBufferAttribute = True

    def __init__(self, interleavedBuffer: InterleavedBuffer, itemSize, offset, normalized = False) -> None:
        super().__init__()

        self._type = 'InterleavedBufferAttribute'

        self.name = ''
        self.data = interleavedBuffer
        self.itemSize = itemSize
        self.offset = offset

        self.normalized = normalized == True


    @property
    def count(self):
        return self.data.count

    @property
    def array(self):
        return self.data.array

    
    @property
    def needsUpdate( self ):
        return self.data.needsUpdate

    @needsUpdate.setter
    def needUpdate( self, value):
        self.data.needsUpdate = value

    
    def clone(self, data):
        if not data:

            #console.log( 'THREE.InterleavedBufferAttribute.clone(): Cloning an interlaved buffer attribute will deinterleave buffer data.' );

            array = []

            for i in range(self.count):
                index = i * self.data.stride + self.offset

                for j in range(self.itemSize):
                    array.append(self.data.array[ index + j ])

            return BufferAttribute( self.data.array.copy(), self.itemSize, self.normalized )

        else:
            if not data.interleavedBuffers:
                data.interleavedBuffers = {}

            if data.interleavedBuffers[ self.data.uuid ] is None:
                    data.interleavedBuffers[ self.data.uuid ] = self.data.clone( data )

            return InterleavedBufferAttribute( data.interleavedBuffers[ self.data.uuid ], self.itemSize, self.offset, self.normalized )