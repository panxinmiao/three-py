from .wgpu_binding import WgpuBinding
from ...structure import Float32Array
from .constants import GPUBindingType, GPUShaderStage, GPUBufferUsage
from .wgpu_buffer_utils import getFloatLength

class WgpuUniformBuffer(WgpuBinding):

    def __init__(self, name, buffer = None) -> None:
        super().__init__(name)

        self.bytesPerElement = Float32Array.bytes_per_element
        self.type = GPUBindingType.UniformBuffer
        self.visibility = GPUShaderStage.VERTEX

        self.usage = GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST

        self.buffer = buffer
        self.bufferGPU = None  # set by the renderer

    
    def getByteLength(self):
        return getFloatLength( self.buffer.byteLength )


    def getBuffer(self):
        return self.buffer


    def update(self):
        return True

    @property
    def isUniformBuffer(self):
        return True
