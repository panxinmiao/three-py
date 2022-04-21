from .wgpu_binding import WgpuBinding
from .constants import GPUBindingType, GPUTextureViewDimension, GPUShaderStage

class WgpuSampledTexture(WgpuBinding):
    
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

    def __init__(self, name, texture = None) -> None:
        super().__init__(name, texture)

        self.dimension = GPUTextureViewDimension.TwoDArray

class WgpuSampled3DTexture(WgpuSampledTexture):

    def __init__(self, name, texture = None) -> None:
        super().__init__(name, texture)
        self.dimension = GPUTextureViewDimension.ThreeD


class WgpuSampledCubeTexture(WgpuSampledTexture):

    def __init__(self, name, texture = None) -> None:
        super().__init__(name, texture)

        self.dimension = GPUTextureViewDimension.Cube
