from .wgpu_binding import WgpuBinding
from .wgpu_buffer_utils import getFloatLength
from ...structure import Float32Array
from .constants import GPUShaderStage, GPUBufferUsage

class WgpuBuffer(WgpuBinding):

    def __init__(self, name, type, buffer=None) -> None:
        super().__init__(name)

        self.bytesPerElement = Float32Array.bytes_per_element
        self.type = type
        self.visibility = GPUShaderStage.VERTEX
        
        self.usage = GPUBufferUsage.COPY_DST

        self.buffer = buffer
        self.bufferGPU = None # set by the renderer

    def getByteLength(self):
        return getFloatLength(self.buffer.byteLength)


    def getBuffer(self):
        return self.buffer


    def update(self):
        return True
