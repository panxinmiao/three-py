from .wgpu_buffer import WgpuBuffer
from .constants import GPUBindingType, GPUBufferUsage


class WgpuStorageBuffer(WgpuBuffer):

    isStorageBuffer = True

    def __init__(self, name, attribute) -> None:
        super().__init__(name, GPUBindingType.StorageBuffer, attribute.array)

        self.usage |= GPUBufferUsage.VERTEX | GPUBufferUsage.STORAGE

        self.attribute = attribute
