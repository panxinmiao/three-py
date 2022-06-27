from .wgpu_buffer import WgpuBuffer
from .constants import GPUBindingType, GPUBufferUsage

class WgpuUniformBuffer(WgpuBuffer):

    isUniformBuffer = True

    def __init__(self, name, buffer = None) -> None:
        super().__init__(name, GPUBindingType.UniformBuffer, buffer)

        self.usage |= GPUBufferUsage.UNIFORM