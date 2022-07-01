from .wgpu_binding import WgpuBinding
from .constants import GPUBindingType, GPUTextureViewDimension, GPUShaderStage

class WgpuSampledTexture(WgpuBinding):

    isSampledTexture = True
    
    def __init__( self, name, texture = None ) -> None:
        super().__init__(name)

        self.texture = texture
        self.dimension = GPUTextureViewDimension.TwoD
        
        self.type = GPUBindingType.SampledTexture
        self.visibility = GPUShaderStage.FRAGMENT

        self.textureGPU = None  # set by the renderer

    def getTexture( self ):
        return self.texture


class WgpuSampledArrayTexture(WgpuSampledTexture):

    isSampledArrayTexture = True

    def __init__(self, name, texture = None) -> None:
        super().__init__(name, texture)

        self.dimension = GPUTextureViewDimension.TwoDArray

class WgpuSampled3DTexture(WgpuSampledTexture):

    isSampled3DTexture = True

    def __init__(self, name, texture = None) -> None:
        super().__init__(name, texture)
        self.dimension = GPUTextureViewDimension.ThreeD


class WgpuSampledCubeTexture(WgpuSampledTexture):

    isSampledCubeTexture = True

    def __init__(self, name, texture = None) -> None:
        super().__init__(name, texture)

        self.dimension = GPUTextureViewDimension.Cube
