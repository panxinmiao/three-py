from .wgpu_binding import WgpuBinding
from .constants import GPUBindingType, GPUBufferUsage

class WgpuStorageBuffer(WgpuBinding):

    def __init__(self, name, attribute) -> None:
        super().__init__(name)

        self.type = GPUBindingType.StorageBuffer

        self.usage = GPUBufferUsage.VERTEX | GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST

        self.attribute = attribute
        self.bufferGPU = None  # set by the renderer

    @property
    def isStorageBuffer(self):
        return True