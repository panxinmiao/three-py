from ..wgpu_sampler import WgpuSampler

class WgpuNodeSampler(WgpuSampler):

    def __init__(self, name, textureNode ) -> None:
        super().__init__(name, textureNode.value )
        self.textureNode = textureNode

    def getTexture(self):
        return self.textureNode.value