import warnings
import math
from .wgpu_uniform_buffer import WgpuUniformBuffer
from ...structure import Float32Array
from .constants import GPUChunkSize
from .wgpu_uniform import WgpuUniform, FloatUniform,Vector2Uniform, Vector3Uniform, Vector4Uniform, Matrix3Uniform, Matrix4Uniform, ColorUniform

class WgpuUniformsGroup(WgpuUniformBuffer):

    isUniformsGroup = True

    def __init__(self, name) -> None:
        super().__init__(name)
        self.uniforms:'list[WgpuUniform]' = []

    @property
    def isUniformsGroup( self ):
        return True

    def addUniform( self, uniform ):
        self.uniforms.append( uniform )

        return self


    def removeUniform( self, uniform ):
        if uniform in self.uniforms:
            self.uniforms.remove(uniform)
    
        return self

    def getBuffer(self):
        buffer = self.buffer
        if buffer is None:
            byteLength = self.getByteLength()

            # buffer = Float32Array.wrap( bytearray(byteLength) )
            buffer = memoryview( bytearray(byteLength) ).cast('f')
            self.buffer = buffer

        return buffer


    def getByteLength(self):

        offset = 0 # global buffer offset in bytes

        for uniform in self.uniforms:
            chunkOffset = offset % GPUChunkSize
            remainingSizeInChunk = GPUChunkSize - chunkOffset

            # conformance tests

            if chunkOffset != 0 and ( remainingSizeInChunk - uniform.boundary ) < 0:

                # check for chunk overflow
                offset += ( GPUChunkSize - chunkOffset )
            
            elif chunkOffset % uniform.boundary != 0:

                # check for correct alignment

                offset += ( chunkOffset % uniform.boundary )

            uniform.offset = ( offset / self.bytesPerElement )
            offset += ( uniform.itemSize * self.bytesPerElement )

        # offset = (int(offset / GPUChunkSize) + 1)*GPUChunkSize
        return math.ceil( offset / GPUChunkSize ) * GPUChunkSize

    def update(self):
        updated = False

        for uniform in self.uniforms:
            if self.updateByType( uniform ) == True:
                updated = True

        return updated


    def updateByType( self, uniform:'WgpuUniform' ):
        return self.updateBuffer( uniform )
        # if isinstance(uniform, FloatUniform):
        #     return self.updateNumber( uniform )
        # if isinstance(uniform, Vector2Uniform):
        #     return self.updateVector2( uniform )
        # if isinstance(uniform, Vector3Uniform):
        #     return self.updateVector3( uniform )
        # if isinstance(uniform, Vector4Uniform):
        #     return self.updateVector4( uniform )
        # if isinstance(uniform, ColorUniform):
        #     return self.updateColor( uniform )
        # if isinstance(uniform, Matrix3Uniform):
        #     return self.updateMatrix3( uniform )
        # if isinstance(uniform, Matrix4Uniform):
        #     return self.updateMatrix4( uniform )

        # warnings.warn( f'THREE.WebGPUUniformsGroup: Unsupported uniform type.{uniform}' )

    def updateBuffer( self, uniform:'WgpuUniform' ):
        updated = False
        a = self.buffer
        v = uniform.getBuffer()
        offset = uniform.offset
        itemSize = uniform.itemSize

        if a[ offset : offset + itemSize ] != v:
            a[ offset : offset + itemSize ] = v
            updated = True

        return updated

    def updateNumber( self, uniform:'WgpuUniform' ):
        updated = False
        a = self.buffer
        v = uniform.getValue()
        offset = uniform.offset

        if a[ offset ] != v:
            a[ offset ] = v
            updated = True

        return updated

    def updateVector2( self, uniform:'WgpuUniform' ):
        updated = False
        a = self.buffer
        v = uniform.getValue()
        offset = uniform.offset

        if a[ offset + 0 ] != v.x or a[ offset + 1 ] != v.y:
            a[ offset + 0 ] = v.x
            a[ offset + 1 ] = v.y

            updated = True

        return updated

    def updateVector3( self, uniform:'WgpuUniform' ):
        updated = False
        a = self.buffer
        v = uniform.getValue()
        offset = uniform.offset

        if a[ offset + 0 ] != v.x or a[ offset + 1 ] != v.y or a[ offset + 2 ] != v.z:
            a[ offset + 0 ] = v.x
            a[ offset + 1 ] = v.y
            a[ offset + 2 ] = v.z

            updated = True

        return updated

    def updateVector4( self, uniform:'WgpuUniform' ):
        updated = False
        a = self.buffer
        v = uniform.getValue()
        offset = uniform.offset

        if a[ offset + 0 ] != v.x or a[ offset + 1 ] != v.y or a[ offset + 2 ] != v.z or a[ offset + 4 ] != v.w:
            a[ offset + 0 ] = v.x
            a[ offset + 1 ] = v.y
            a[ offset + 2 ] = v.z
            a[ offset + 3 ] = v.w

            updated = True

        return updated

    def updateColor( self, uniform:'WgpuUniform' ):
        updated = False
        a = self.buffer
        c = uniform.getValue()
        offset = uniform.offset

        if a[ offset + 0 ] != c.r or a[ offset + 1 ] != c.g or a[ offset + 2 ] != c.b:
            a[ offset + 0 ] = c.r
            a[ offset + 1 ] = c.g
            a[ offset + 2 ] = c.b
            updated = True

        return updated

    def updateMatrix3( self, uniform:'WgpuUniform' ):
        updated = False
        a = self.buffer
        e = uniform.getValue().elements
        offset = uniform.offset

        if (a[ offset + 0 ] != e[ 0 ] or a[ offset + 1 ] != e[ 1 ] or a[ offset + 2 ] != e[ 2 ] or
            a[ offset + 4 ] != e[ 3 ] or a[ offset + 5 ] != e[ 4 ] or a[ offset + 6 ] != e[ 5 ] or
            a[ offset + 8 ] != e[ 6 ] or a[ offset + 9 ] != e[ 7 ] or a[ offset + 10 ] != e[ 8 ] ):

            a[ offset + 0 ] = e[ 0 ]
            a[ offset + 1 ] = e[ 1 ]
            a[ offset + 2 ] = e[ 2 ]
            a[ offset + 4 ] = e[ 3 ]
            a[ offset + 5 ] = e[ 4 ]
            a[ offset + 6 ] = e[ 5 ]
            a[ offset + 8 ] = e[ 6 ]
            a[ offset + 9 ] = e[ 7 ]
            a[ offset + 10 ] = e[ 8 ]

            updated = True

        return updated

    def updateMatrix4( self, uniform:'WgpuUniform' ):
        updated = False
        a = self.buffer
        offset = uniform.offset
        e = uniform.getValue().elements
        if arraysEqual( a, e, offset ) == False:
            a[offset: offset + 16] = e[0:16]
            # a.set( e, offset )

            updated = True
        
        return updated


def arraysEqual( a, b, offset ):
    for i in range(len(b)):
        if a[ offset + i ] != b[ i ]:
            return False

    return True

