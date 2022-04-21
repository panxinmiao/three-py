from ..wgpu_uniforms_group import WgpuUniformsGroup
from ..constants import GPUShaderStage

class WgpuNodeUniformsGroup(WgpuUniformsGroup):

    def __init__(self, shaderStage ) -> None:
        super().__init__('nodeUniforms')

        shaderStageVisibility = None

        if shaderStage == 'vertex':
            shaderStageVisibility = GPUShaderStage.VERTEX
        elif shaderStage == 'fragment':
            shaderStageVisibility = GPUShaderStage.FRAGMENT

        self.setVisibility( shaderStageVisibility )