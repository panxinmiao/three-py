from .wgpu_binding import WgpuBinding
from .constants import GPUBindingType
import wgpu

class WgpuSampler(WgpuBinding):

    isSampler = True
    
    def __init__(self, name, texture) -> None:
        super().__init__(name)

        self.texture = texture

        self.type = GPUBindingType.Sampler
        self.visibility = wgpu.ShaderStage.FRAGMENT
        self.samplerGPU = None

    def getTexture( self ):
        return self.texture

    