import uuid
from ..constants import StaticDrawUsage
from ..structure import NoneAttribute, TypedArray

class InterleavedBuffer(NoneAttribute):

    isInterleavedBuffer = True

    def __init__(self, ary: TypedArray, stride) -> None:
        self.array = ary
        self.stride = stride

        self.count = 0 if ary is None else len(ary)/stride
        #self.count = array !== undefined ? array.length / stride : 0

        self.usage = StaticDrawUsage
        self.updateRange = { 'offset': 0, 'count': - 1 }

        self.version = 0

        #self._need_update = False

        self.uuid = uuid.uuid1()

    @property
    def needsUpdate( self ):
        return False

    @needsUpdate.setter
    def needsUpdate( self, value):
        #self._need_update = value
        if value:
            self.version += 1

    def onUploadCallback(self):
        pass

    def onUpload(self, callback):
        self.onUploadCallback = callback
        return self


    def setUsage( self, value ):
        self.usage = value
        return self

    def copy( self, source:'InterleavedBuffer' ):
        self.array = source.array.copy()
        self.count = source.count
        self.stride = source.stride
        
        self.usage = source.usage

        return self

    def copyAt(self, index1, attribute, index2 ):
        index1 *= self.stride
        index2 *= attribute.stride

        for i in range(self.stride):
            self.array[ index1 + i ] = attribute.array[ index2 + i ]

        return self


    def set(self, value, offset = 0):
        self.array[offset] = value
        return self

    def clone(self, data ):
        
        if data.arrayBuffers is None:
            data.arrayBuffers = {}

        buffer_address = self.array.uuid

        if data.arrayBuffers[ buffer_address ] is None:
            data.arrayBuffers[ buffer_address ] = self.array.range_buffer()

        # ary = array(self.array.typecode).frombytes(data.arrayBuffers[ buffer_address ])

        ary = self.array.__class__.wrap(data.arrayBuffers[ buffer_address ])

        #ary  = copy(data.arrayBuffers[ buffer_address ])

        ib = InterleavedBuffer( ary, self.stride )

        ib.setUsage( self.usage )
        
        return ib
