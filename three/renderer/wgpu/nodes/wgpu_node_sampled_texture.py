from ..wgpu_sampled_texture import WgpuSampledTexture, WgpuSampledCubeTexture 

class WgpuNodeSampledTexture(WgpuSampledTexture):

    def __init__(self, name, textureNode ) -> None:
        super().__init__(name, textureNode.value)
        self.textureNode = textureNode

    def getTexture(self):
        return self.textureNode.value

class WgpuNodeSampledCubeTexture(WgpuSampledCubeTexture):
    def __init__(self, name, textureNode ) -> None:
        super().__init__(name, textureNode.value)
        self.textureNode = textureNode

    def getTexture(self):
        return self.textureNode.value