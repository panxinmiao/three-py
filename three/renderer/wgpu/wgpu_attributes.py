from weakref import WeakKeyDictionary
from .constants import GPUBufferUsage
from ...structure import Dict
import three
import wgpu
import wgpu.backends.rs

class WgpuAttributes:

    def __init__(self, device: 'wgpu.GPUDevice') -> None:
        self.buffers = WeakKeyDictionary()
        self.device = device

    def get(self, attribute: three.BufferAttribute):
        #if attribute.isInterleavedBufferAttribute:
        if attribute._type == 'InterleavedBufferAttribute':
            attribute = attribute.data
        
        return self.buffers.get( attribute )

    def remove( self, attribute: three.BufferAttribute ):

        if attribute._type == 'InterleavedBufferAttribute':
            attribute = attribute.data
        
        data = self.buffers.get( attribute )

        if data:
            self._destroyBuffers( data )
            self.buffers.pop( attribute )

    def update( self, attribute: three.BufferAttribute, isIndex = False, usage = None ):
        if attribute._type == 'InterleavedBufferAttribute':
            attribute = attribute.data

        data = self.buffers.get( attribute )
   
        if data is None:
            if usage is None:
                usage = GPUBufferUsage.INDEX if isIndex else GPUBufferUsage.VERTEX
            
            data = self._createBuffer( attribute, usage )

            self.buffers[attribute]  = data

        elif usage and usage != data.usage:
            self._destroyBuffers( data )
            data = self._createBuffer( attribute, usage )
            self.buffers.set( attribute, data )

        elif data.version < attribute.version:
            self._writeBuffer( data.buffer, attribute )
            data.version = attribute.version

    def getArrayBuffer( self, attribute ) -> memoryview:
        data = self.get( attribute )
        device = self.device

        gpuBuffer = data.buffer
        size = gpuBuffer.size

        gpuReadBuffer = data.readBuffer
        
        if gpuReadBuffer is None:
            gpuReadBuffer = device.create_buffer(
                size = size,
                usage = GPUBufferUsage.COPY_DST | GPUBufferUsage.MAP_READ
            )

            data.readBuffer = gpuReadBuffer

        cmdEncoder: wgpu.GPUCommandEncoder = device.create_command_encoder()

        cmdEncoder.copy_buffer_to_buffer(
            gpuBuffer,
            0,
            gpuReadBuffer,
            0,
            size
        )

        gpuCommands = cmdEncoder.finish()
        device.queue.submit( [ gpuCommands ] )

        arrayBuffer = gpuReadBuffer.map_read()

        return arrayBuffer


    def _createBuffer( self, attribute: three.BufferAttribute, usage ):
        ary = attribute.array
        size = ary.byteLength + ( ( 4 - ( ary.byteLength % 4 ) ) % 4 );  # ensure 4 byte alignment, see #20441

        buffer = ary.range_buffer()

        if ary.byteLength < size:
            buffer = (buffer if isinstance(buffer, bytearray) else bytearray(buffer)) + bytearray(size - ary.byteLength)

        buffer: wgpu.GPUBuffer = self.device.create_buffer_with_data(
            data = buffer, usage = usage | GPUBufferUsage.COPY_SRC | GPUBufferUsage.COPY_DST       #, mapped_at_creation = True
        )

        # buffer = self.device.createBuffer( {
        #    'size': size,
        #    'usage': usage | GPUBufferUsage.COPY_DST,
        #    'mappedAtCreation': True,
        # } )

        #buffer.get_mapped_range()
        # array.constructor( buffer.getMappedRange() ).set( ary )
        # buffer.unmap()

        attribute.onUploadCallback()
        
        return Dict({
            'version': attribute.version,
            'buffer': buffer,
            'readBuffer': None,
            'usage': usage
        })


    def _writeBuffer( self, buffer, attribute: three.BufferAttribute ):
        array = attribute.array
        updateRange = attribute.updateRange

        if updateRange['count'] == - 1:
            
            # Not using update ranges
            self.device.queue.write_buffer(
                buffer,
                0,
                array.buffer,
                0
            )

        else:
            self.device.queue.write_buffer(
                buffer,
                0,
                array.buffer,
                updateRange.offset * array.bytes_per_element,
                updateRange.count * array.bytes_per_element
            )
            
            updateRange.count = - 1; # reset range

    def _destroyBuffers( self, data ):
        data.buffer.destroy()
        if data.readBuffer is not None:
            data.readBuffer.destroy()
