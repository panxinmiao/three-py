import warnings
from .material import Material
from ..structure import Dict

class ShaderMaterial(Material):

    def __init__(self, parameters = None) -> None:
        super().__init__()
        if type(parameters) == dict:
            parameters = Dict(parameters)


        self.type = 'ShaderMaterial'

        self.defines = {}
        self.uniforms = {}

        self.vertexShader = None # default_vertex
        self.fragmentShader = None # default_fragment

        self.linewidth = 1

        self.wireframe = False
        self.wireframeLinewidth = 1

        self.fog = False  # set to use scene fog
        self.lights = False  # set to use scene lights
        self.clipping = False  # set to use user-defined clipping planes

        self.extensions = {
            'derivatives': False, # set to use derivatives
            'fragDepth': False, # set to use fragment depth values
            'drawBuffers': False, # set to use draw buffers
            'shaderTextureLOD': False # set to use shader texture LOD
        }

        # When rendered geometry doesn't include these attributes but the material does,
        # use these default values in WebGL. This avoids errors when buffer data is missing.
        self.defaultAttributeValues = {
            'color': [ 1, 1, 1 ],
            'uv': [ 0, 0 ],
            'uv2': [ 0, 0 ]
        }

        self.index0AttributeName = None
        self.uniformsNeedUpdate = False

        self.glslVersion = None

        if parameters:
            if parameters.attributes:
                warnings.warn( 'THREE.ShaderMaterial: attributes should now be defined in THREE.BufferGeometry instead.' )

            self.setValues( parameters )


    def copy( self, source:'ShaderMaterial' ):

        super().copy( source )

        self.fragmentShader = source.fragmentShader
        self.vertexShader = source.vertexShader

        # from ..renderer.shaders.uniforms_util import cloneUniforms
        # self.uniforms = cloneUniforms( source.uniforms )

        self.defines = source.defines.copy()

        self.wireframe = source.wireframe
        self.wireframeLinewidth = source.wireframeLinewidth

        self.lights = source.lights
        self.clipping = source.clipping

        self.extensions = source.extensions.copy()

        self.glslVersion = source.glslVersion

        return self