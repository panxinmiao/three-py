from warnings import warn
import three
import wgpu
from ...structure import Dict
from .constants import ( GPUVertexFormat, GPUInputStepMode, GPUBlendFactor, GPUBlendOperation, BlendColorFactor, OneMinusBlendColorFactor, 
                            GPUColorWriteFlags, GPUCompareFunction, GPUIndexFormat, GPUFrontFace, GPUCullMode, GPUStencilOperation )

from ...constants import ( NoBlending, NormalBlending, AdditiveBlending, SubtractiveBlending, MultiplyBlending, CustomBlending, 
                            ZeroFactor, OneFactor, SrcColorFactor, OneMinusSrcColorFactor, SrcAlphaFactor, OneMinusSrcAlphaFactor, DstColorFactor,
                            OneMinusDstColorFactor, DstAlphaFactor, OneMinusDstAlphaFactor, SrcAlphaSaturateFactor,
                            AddEquation, SubtractEquation, ReverseSubtractEquation, MinEquation, MaxEquation, 
                            NeverDepth, AlwaysDepth, LessDepth, LessEqualDepth, EqualDepth, GreaterEqualDepth, GreaterDepth, NotEqualDepth, FrontSide, BackSide, DoubleSide, 
                            NeverStencilFunc, AlwaysStencilFunc, LessStencilFunc, LessEqualStencilFunc, EqualStencilFunc, GreaterEqualStencilFunc, GreaterStencilFunc, NotEqualStencilFunc, 
                            KeepStencilOp, ZeroStencilOp, ReplaceStencilOp, InvertStencilOp, IncrementStencilOp, DecrementStencilOp, IncrementWrapStencilOp, DecrementWrapStencilOp )
# from .wgpu_renderer import WgpuRenderer

class WgpuRenderPipeline():

    def __init__(self, device:'wgpu.GPUDevice', renderer:'three.WgpuRenderer', sampleCount) -> None:
        self._device = device
        self._renderer = renderer
        self._sampleCount = sampleCount

        self.cacheKey = None
        self.stageVertex = None
        self.stageFragment = None
        self.shaderAttributes = None
        self.usedTimes = 0

    def init(self, cacheKey, stageVertex, stageFragment, object, nodeBuilder):
        material:'three.Material' = object.material
        geometry:'three.Geometry' = object.geometry

        # determine shader attributes
        shaderAttributes = self._getShaderAttributes( nodeBuilder, geometry )

        # vertex buffers
        vertexBuffers = []

        bindings = nodeBuilder.getBindings()
        
        for attribute in shaderAttributes:
            name = attribute.name
            geometryAttribute = geometry.getAttribute( name )
            stepMode = GPUInputStepMode.Instance if geometryAttribute and geometryAttribute.isInstancedBufferAttribute else GPUInputStepMode.Vertex

            vertexBuffers.append( {
                'array_stride': attribute.arrayStride,
                'attributes': [{'shader_location': attribute.slot, 'offset': attribute.offset, 'format': attribute.format}],
                'step_mode': stepMode
            } )


        self.cacheKey = cacheKey
        self.shaderAttributes = shaderAttributes
        self.stageVertex = stageVertex
        self.stageFragment = stageFragment

        # blending
        
        alphaBlend = {
            'src_factor': GPUBlendFactor.One,
            'dst_factor': GPUBlendFactor.Zero,
            'operation': GPUBlendOperation.Add
        }
        colorBlend = {
            'src_factor': GPUBlendFactor.One,
            'dst_factor': GPUBlendFactor.Zero,
            'operation': GPUBlendOperation.Add
        }

        if material.transparent == True and material.blending != NoBlending:
            alphaBlend = self._getAlphaBlend( material )
            colorBlend = self._getColorBlend( material )

        # stencil

        stencilFront = {}
        
        if material.stencilWrite == True:
            stencilFront = {
                'compare': self._getStencilCompare( material ),
                'fail_op': self._getStencilOperation( material.stencilFail ),
                'depth_fail_op': self._getStencilOperation( material.stencilZFail ),
                'pass_op': self._getStencilOperation( material.stencilZPass )
            }

        primitiveState = self._getPrimitiveState( object, material )
        colorWriteMask = self._getColorWriteMask( material )
        depthCompare = self._getDepthCompare( material )
        colorFormat = self._renderer.getCurrentColorFormat()
        depthStencilFormat = self._renderer.getCurrentDepthStencilFormat()
        
        _vertex = {}
        _vertex.update(stageVertex.stage, buffers = vertexBuffers)
        
        _fragment = {}
        _fragment.update(stageFragment.stage,  targets = [ {
            'format': colorFormat,
            'blend': {
                'alpha': alphaBlend,
                'color': colorBlend
            },
            'write_mask': colorWriteMask
        } ] )

        depthStencil ={
            'format': depthStencilFormat,
            'depth_write_enabled': material.depthWrite,
            'depth_compare': depthCompare,
            'stencil_front': stencilFront,
            'stencil_back': stencilFront, # three.js does not provide an API to configure the back function (gl.stencilFuncSeparate() was never used)
            'stencil_read_mask': material.stencilFuncMask,
            'stencil_write_mask': material.stencilWriteMask
        }
    
        _layout= self._getPipelineLayout(bindings)
        
        self.pipeline = self._device.create_render_pipeline(
            layout= _layout,
            vertex = _vertex,
            fragment = _fragment,
            primitive = primitiveState,
            depth_stencil = depthStencil,
            multisample = {
                'count': self._sampleCount
            }
        )

    def _getAlphaBlend( self, material ):
        blending = material.blending
        premultipliedAlpha = material.premultipliedAlpha
        alphaBlend = None

        if blending == NormalBlending:
            if premultipliedAlpha == False:
                alphaBlend = {
                    'src_factor': GPUBlendFactor.One,
                    'dst_factor': GPUBlendFactor.OneMinusSrcAlpha,
                    'operation': GPUBlendOperation.Add
                }
        elif blending == AdditiveBlending:
            pass
        elif blending == SubtractiveBlending:
            if premultipliedAlpha == True:
                alphaBlend = {
                    'src_factor': GPUBlendFactor.OneMinusSrcColor,
                    'dst_factor': GPUBlendFactor.OneMinusSrcAlpha,
                    'operation': GPUBlendOperation.Add
                }
        elif blending == MultiplyBlending:
            if premultipliedAlpha == True:
                alphaBlend = {
                    'src_factor': GPUBlendFactor.Zero,
                    'dst_factor': GPUBlendFactor.SrcAlpha,
                    'operation': GPUBlendOperation.Add
                }
        elif blending == CustomBlending:
            blendSrcAlpha = material.blendSrcAlpha
            blendDstAlpha = material.blendDstAlpha
            blendEquationAlpha = material.blendEquationAlpha

            if blendSrcAlpha and blendDstAlpha and blendEquationAlpha:
                alphaBlend = {
                    'src_factor': self._getBlendFactor( blendSrcAlpha ),
                    'dst_factor': self._getBlendFactor( blendDstAlpha ),
                    'operation': self._getBlendOperation( blendEquationAlpha )
                }
        else:
            warn(f'THREE.WebGPURenderer: Blending not supported.{blending}' )

        return alphaBlend


    def _getBlendFactor( self, blend ):
        if blend == ZeroFactor:
            return GPUBlendFactor.Zero
            
        if blend == ZeroFactor:
            return GPUBlendFactor.Zero

        if blend == OneFactor:
            return GPUBlendFactor.One

        if blend == SrcColorFactor:
            return GPUBlendFactor.SrcColor

        if blend == OneMinusSrcColorFactor:
            return GPUBlendFactor.OneMinusSrcColor

        if blend == SrcAlphaFactor:
            return GPUBlendFactor.SrcAlpha

        if blend == OneMinusSrcAlphaFactor:
            return GPUBlendFactor.OneMinusSrcAlpha

        if blend == DstColorFactor:
            return GPUBlendFactor.DstColor

        if blend == OneMinusDstColorFactor:
            return GPUBlendFactor.OneMinusDstColor

        if blend == DstAlphaFactor:
            return GPUBlendFactor.DstAlpha

        if blend == OneMinusDstAlphaFactor:
            return GPUBlendFactor.OneMinusDstAlpha

        if blend == SrcAlphaSaturateFactor:
            return GPUBlendFactor.SrcAlphaSaturated

        if blend == BlendColorFactor:
            return GPUBlendFactor.BlendColor

        if blend == OneMinusBlendColorFactor:
            return GPUBlendFactor.OneMinusBlendColor

        warn( f'THREE.WebGPURenderer: Blend factor not supported.{blend}' )
        return None

    def _getBlendOperation( self, blendEquation ):
        
        if blendEquation == AddEquation:
            return GPUBlendOperation.Add

        if blendEquation == SubtractEquation:
            return GPUBlendOperation.Subtract

        if blendEquation == ReverseSubtractEquation:
            return GPUBlendOperation.ReverseSubtract

        if blendEquation == MinEquation:
            return GPUBlendOperation.Min

        if blendEquation == MaxEquation:
            return GPUBlendOperation.Max
        
        warn( f'THREE.WebGPURenderer: Blend equation not supported.{blendEquation}' )
    
        return None


    def _getColorBlend( self, material ):
        blending = material.blending
        premultipliedAlpha = material.premultipliedAlpha

        if blending == NormalBlending:
            return {
                'src_factor': GPUBlendFactor.One if premultipliedAlpha else GPUBlendFactor.SrcAlpha,
                'dst_factor': GPUBlendFactor.OneMinusSrcAlpha,
                'operation': GPUBlendOperation.Add
            }

        if blending == AdditiveBlending:
            return {
                'src_factor': GPUBlendFactor.One if premultipliedAlpha else GPUBlendFactor.SrcAlpha,
                'operation': GPUBlendOperation.Add
            }
        
        if blending == SubtractiveBlending:
            return {
                'src_factor': GPUBlendFactor.Zero,
                'dst_factor': GPUBlendFactor.Zero if premultipliedAlpha else GPUBlendFactor.OneMinusSrcColor,
                'operation': GPUBlendOperation.Add
            }
        
        if blending == MultiplyBlending:
            return {
                'src_factor': GPUBlendFactor.Zero,
                'dst_factor': GPUBlendFactor.SrcColor,
                'operation': GPUBlendOperation.Add
            }

        if blending == CustomBlending:
            return {
                'src_factor': self._getBlendFactor( material.blendSrc ),
                'dst_factor': self._getBlendFactor( material.blendDst ),
                'operation': self._getBlendOperation( material.blendEquation )
            }

        warn( f'THREE.WebGPURenderer: Blending not supported.{blending}' )

        return {
            'src_factor': None,
            'dst_factor': None,
            'operation': None
        }

    def _getColorWriteMask( self, material:'three.Material' ):
        return GPUColorWriteFlags.All if material.colorWrite == True else GPUColorWriteFlags.NONE

    def _getDepthCompare( self, material:'three.Material' ):
        depthCompare = None

        if material.depthTest == False:
            depthCompare = GPUCompareFunction.Always
        else:
            depthFunc = material.depthFunc
            if depthFunc == NeverDepth:
                depthCompare = GPUCompareFunction.Never

            elif depthFunc == AlwaysDepth:
                depthCompare = GPUCompareFunction.Always

            elif depthFunc == LessDepth:
                depthCompare = GPUCompareFunction.Less

            elif depthFunc == LessEqualDepth:
                depthCompare = GPUCompareFunction.LessEqual

            elif depthFunc == EqualDepth:
                depthCompare = GPUCompareFunction.Equal

            elif depthFunc == GreaterEqualDepth:
                depthCompare = GPUCompareFunction.GreaterEqual

            elif depthFunc == GreaterDepth:
                depthCompare = GPUCompareFunction.Greater

            elif depthFunc == NotEqualDepth:
                depthCompare = GPUCompareFunction.NotEqual

            else:
                warn( f'THREE.WebGPURenderer: Invalid depth function.{depthFunc}' )
        
        return depthCompare

    def _getPrimitiveState( self, object, material:'three.Material' ):
        descriptor = {}
        
        descriptor['topology'] = self._renderer.getPrimitiveTopology( object )

        if object.isLine == True and object.isLineSegments != True:
            geometry = object.geometry
            count = geometry.index.count if geometry.index else geometry.attributes.position.count
            descriptor['strip_index_format'] = GPUIndexFormat.Uint32 if count > 65535 else GPUIndexFormat.Uint16  # define data type for primitive restart value

        if material.side == FrontSide:
            descriptor['front_face'] = GPUFrontFace.CW
            descriptor['cull_mode'] = GPUCullMode.Front
        
        elif material.side == BackSide:
            descriptor['front_face'] = GPUFrontFace.CW
            descriptor['cull_mode'] = GPUCullMode.Back

        elif material.side == DoubleSide:
            descriptor['front_face'] = GPUFrontFace.CW
            descriptor['cull_mode'] = GPUCullMode.NONE

        else:
            warn( f'THREE.WebGPURenderer: Unknown Material.side value.{ material.side }' )

        return descriptor

    def _getStencilCompare( self, material ):

        #let stencilCompare;

        stencilFunc = material.stencilFunc

        if stencilFunc == NeverStencilFunc:
            return GPUCompareFunction.Never
        
        elif stencilFunc == AlwaysStencilFunc:
            return GPUCompareFunction.Always

        elif stencilFunc == LessStencilFunc:
            return GPUCompareFunction.Less

        elif stencilFunc == LessEqualStencilFunc:
            return GPUCompareFunction.LessEqual

        elif stencilFunc == EqualStencilFunc:
            return GPUCompareFunction.Equal

        elif stencilFunc == GreaterEqualStencilFunc:
            return GPUCompareFunction.GreaterEqual

        elif stencilFunc == GreaterStencilFunc:
            return GPUCompareFunction.Greater

        elif stencilFunc == NotEqualStencilFunc:
            return GPUCompareFunction.NotEqual

        else:
            warn( f'THREE.WebGPURenderer: Invalid stencil function.{stencilFunc}' )
            return None

    def _getStencilOperation( self, op ):

        if op == KeepStencilOp:
            return GPUStencilOperation.Keep

        elif op == ZeroStencilOp:
            return GPUStencilOperation.Zero

        elif op == ReplaceStencilOp:
            return GPUStencilOperation.Replace

        elif op == InvertStencilOp:
            return GPUStencilOperation.Invert

        elif op == IncrementStencilOp:
            return GPUStencilOperation.IncrementClamp

        elif op == DecrementStencilOp:
            return GPUStencilOperation.DecrementClamp

        elif op == IncrementWrapStencilOp:
            return GPUStencilOperation.IncrementWrap

        elif op == DecrementWrapStencilOp:
            return GPUStencilOperation.DecrementWrap

        else:
            warn( f'THREE.WebGPURenderer: Invalid stencil operation.{op}' )

        return None


    def _getVertexFormat( self, type, bytesPerElement ):

        #float
        if type == 'float':
            return GPUVertexFormat.Float32

        if type == 'vec2':
            if bytesPerElement == 2:
                return GPUVertexFormat.Float16x2
            else:
                return GPUVertexFormat.Float32x2

        if type == 'vec3':
            return GPUVertexFormat.Float32x3

        if type == 'vec4':
            if bytesPerElement == 2:
                return GPUVertexFormat.Float16x4
            else:
                return GPUVertexFormat.Float32x4

        #int
        if type == 'int':
            return GPUVertexFormat.Sint32

        if type == 'ivec2':
            if bytesPerElement == 1:
                return GPUVertexFormat.Sint8x2
            elif bytesPerElement == 2:
                return GPUVertexFormat.Sint16x2
            else: 
                return GPUVertexFormat.Sint32x2

        if type == 'ivec3':
            return GPUVertexFormat.Sint32x3

        if type == 'ivec4':

            if bytesPerElement == 1:
                return GPUVertexFormat.Sint8x4
            elif bytesPerElement == 2:
                return GPUVertexFormat.Sint16x4
            else:
                return GPUVertexFormat.Sint32x4

        #uint
        if type == 'uint':
            return GPUVertexFormat.Uint32

        if type == 'uvec2':
            if bytesPerElement == 1:
                return GPUVertexFormat.Uint8x2
            elif bytesPerElement == 2:
                return GPUVertexFormat.Uint16x2
            else:
                return GPUVertexFormat.Uint32x2

        if type == 'uvec3':
            return GPUVertexFormat.Uint32x3

        if type == 'uvec4':
            if bytesPerElement == 1:
                return GPUVertexFormat.Uint8x4
            elif bytesPerElement == 2:
                return GPUVertexFormat.Uint16x4
            else:
                return GPUVertexFormat.Uint32x4

        warn( f'THREE.WebGPURenderer: Shader variable type not supported yet.{type}' )
        return None

    def _getShaderAttributes( self, nodeBuilder, geometry:'three.Geometry' ):

        nodeAttributes = nodeBuilder.attributes
        attributes = []

        for slot in range(len(nodeAttributes)):
            nodeAttribute = nodeAttributes[ slot ]

            name = nodeAttribute.name
            type = nodeAttribute.type

            geometryAttribute = geometry.getAttribute( name )
            bytesPerElement = geometryAttribute.array.bytes_per_element

            # arrayStride = self._getArrayStride( type, bytesPerElement )
            format = self._getVertexFormat( type, bytesPerElement )

            arrayStride = geometryAttribute.itemSize * bytesPerElement
            offset = 0

            if geometryAttribute.isInterleavedBufferAttribute:
                # @TODO: It can be optimized for "vertexBuffers" on RenderPipeline
                arrayStride = geometryAttribute.data.stride * bytesPerElement
                offset = geometryAttribute.offset * bytesPerElement

            attributes.append( Dict({
                'name':name,
                'arrayStride':arrayStride,
                'offset':offset,
                'format':format,
                'slot':slot,
            }) )

        return attributes

    def _getPipelineLayout( self, bindings ):
        bind_group_layouts = []

        bindingPoint = 0
        entries = []

        for binding in bindings:
            if binding.isUniformBuffer:
                entries.append( { 
                    'binding': bindingPoint,
                    'visibility': binding.visibility,
                    "buffer": {
                        "type": 'uniform',
                        "has_dynamic_offset": False,
                        "min_binding_size": 0,
                    }
                })

            elif binding.isStorageBuffer:
                entries.append( { 
                    'binding': bindingPoint,
                    'visibility': binding.visibility,
                    "buffer": {
                        "type": 'storage',
                        "has_dynamic_offset": False,
                        "min_binding_size": 0,
                    }
                })

            elif binding.isSampler:
                entries.append( { 
                    'binding': bindingPoint,
                    'visibility': binding.visibility,
                    "sampler": {
                        "type": "filtering"   # TODO : filtering, comparison
                    }
                })

            elif binding.isSampledTexture:
                entries.append( { 
                    'binding': bindingPoint,
                    'visibility': binding.visibility,
                    "texture": {
                        "view_dimension": binding.dimension
                    }
                })
    
            bindingPoint += 1

        bind_group_layout = self._device.create_bind_group_layout( entries= entries)
        bind_group_layouts.append(bind_group_layout)
        pipeline_layout = self._device.create_pipeline_layout(bind_group_layouts=bind_group_layouts)
        return pipeline_layout