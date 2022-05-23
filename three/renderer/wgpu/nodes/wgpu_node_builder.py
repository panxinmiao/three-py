import re
from typing import Iterable

from ....structure import Dict

from three.nodes import NodeBuilder, WGSLNodeParser, CodeNode
from ..wgpu_buffer_utils import getStrideLength, getVectorLength
from .wgpu_node_sampler import WgpuNodeSampler
from .wgpu_node_sampled_texture import WgpuNodeSampledTexture, WgpuNodeSampledCubeTexture
from .wgpu_node_uniforms_group import WgpuNodeUniformsGroup
from ..wgpu_uniform_buffer import WgpuUniformBuffer
from .wgpu_node_uniform import FloatNodeUniform, Vector2NodeUniform, Vector3NodeUniform, Vector4NodeUniform, ColorNodeUniform, Matrix3NodeUniform, Matrix4NodeUniform

from three.nodes.materials import fromMaterial

_flow_p = re.compile(r'.*;\s*$')

supports = {
	'instance': True
}

wgslTypeLib = {
	'float': 'f32',
	'int': 'i32',
    'uint': 'u32',
	'bool': 'bool',

	'vec2': 'vec2<f32>',
    'ivec2': 'vec2<i32>',
	'uvec2': 'vec2<u32>',
	'bvec2': 'vec2<bool>',

	'vec3': 'vec3<f32>',
    'ivec3': 'vec3<i32>',
	'uvec3': 'vec3<u32>',
	'bvec3': 'vec3<bool>',

	'vec4': 'vec4<f32>',
    'ivec4': 'vec4<i32>',
	'uvec4': 'vec4<u32>',
	'bvec4': 'vec4<bool>',

	'mat3': 'mat3x3<f32>',
    'imat3': 'mat3x3<i32>',
	'umat3': 'mat3x3<u32>',
	'bmat3': 'mat3x3<bool>',

	'mat4': 'mat4x4<f32>',
    'imat4': 'mat4x4<i32>',
	'umat4': 'mat4x4<u32>',
	'bmat4': 'mat4x4<bool>'
}

wgslMethods = {
	'dFdx': 'dpdx',
	'dFdy': 'dpdy',
    'inversesqrt': 'inverseSqrt'
}

wgslPolyfill = {
	'lessThanEqual': CodeNode( '''
fn lessThanEqual( a : vec3<f32>, b : vec3<f32> ) -> vec3<bool> {
	return vec3<bool>( a.x <= b.x, a.y <= b.y, a.z <= b.z );
}
''' ),
	'mod': CodeNode( '''
fn mod( x : f32, y : f32 ) -> f32 {
	return x - y * floor( x / y );
}
''' ),
#     'smoothstep':  CodeNode( '''
# fn smoothstep( low : f32, high : f32, x : f32 ) -> f32 {
#     let t = clamp( ( x - low ) / ( high - low ), 0.0, 1.0 );
#     return t * t * ( 3.0 - 2.0 * t );
# }
# ''' ),
	'repeatWrapping': CodeNode( '''
fn repeatWrapping( uv : vec2<f32>, dimension : vec2<i32> ) -> vec2<i32> {
	let uvScaled = vec2<i32>( uv * vec2<f32>( dimension ) );
	return ( ( uvScaled % dimension ) + dimension ) % dimension;
}
''' )
}

class WgpuNodeBuilder(NodeBuilder):

    def __init__(self, object, renderer) -> None:
        super().__init__(object, renderer, WGSLNodeParser())

        self.lightNode = None
        self.fogNode = None

        self.bindings = {'vertex': [], 'fragment': []}
        self.bindingsOffset = {'vertex': 0, 'fragment': 0}

        self.uniformsGroup = {}

        self.builtins = set()


    def build(self):
        fromMaterial(self.material).build(self)
        return super().build()

    def addFlowCode( self, code ):
        if not _flow_p.match(code):
            code += ';'
        super().addFlowCode( code + '\n\t' )

    def getSampler( self, textureProperty, uvSnippet, shaderStage = None ):

        if shaderStage is None:
            shaderStage =  self.shaderStage

        if shaderStage == 'fragment':
            return f'textureSample( {textureProperty}, {textureProperty}_sampler, {uvSnippet} )'
        else:
            self._include( 'repeatWrapping' )
            dimension = f'textureDimensions( {textureProperty}, 0 )'
            
            return f'textureLoad( {textureProperty}, repeatWrapping( {uvSnippet}, {dimension} ), 0 )'

    def getSamplerBias( self, textureProperty, uvSnippet, biasSnippet, shaderStage = None ):
        if shaderStage is None:
            shaderStage =  self.shaderStage

        if shaderStage == 'fragment':
            return f'textureSampleBias( {textureProperty}, {textureProperty}_sampler, {uvSnippet}, {biasSnippet} )'

        else:
            self._include( 'repeatWrapping' )
            dimension = f'textureDimensions( {textureProperty}, 0 )'
            return f'textureLoad( {textureProperty}, repeatWrapping( {uvSnippet}, {dimension} ), i32( {biasSnippet} ) )'


    def getTexture( self, textureProperty, uvSnippet, shaderStage = None ):
        shaderStage = shaderStage or self.shaderStage
        return self.getSampler( textureProperty, uvSnippet, shaderStage )

    def getTextureBias( self, textureProperty, uvSnippet, biasSnippet, shaderStage = None ):
        if shaderStage is None:
            shaderStage =  self.shaderStage

        return self.getSamplerBias( textureProperty, uvSnippet, biasSnippet, shaderStage )

    
    def getCubeTexture( self, textureProperty, uvSnippet, shaderStage = None ):
        shaderStage = shaderStage or self.shaderStage
        return self.getSampler( textureProperty, uvSnippet, shaderStage )

    
    def getCubeTextureBias( self, textureProperty, uvSnippet, biasSnippet, shaderStage = None ):
        if shaderStage is None:
            shaderStage =  self.shaderStage

        return self.getSamplerBias( textureProperty, uvSnippet, biasSnippet, shaderStage )


    def getPropertyName( self, node, shaderStage = None):
        if shaderStage is None:
            shaderStage =  self.shaderStage 

        if node.isNodeVary:
            if shaderStage == 'vertex':
                return f'NodeVarys.{ node.name }'

        elif node.isNodeUniform:
            name = node.name
            type = node.type

            if type == 'texture' or type == 'cubeTexture':
                return name
            elif type == 'buffer':
                return f'NodeBuffer_{node.node.id}.{name}'
            else:
                return f'NodeUniforms.{name}'

        return super().getPropertyName( node )

    
    def getBindings(self):
        bindings = self.bindings
        return bindings['vertex'] + bindings['fragment']

    
    def getUniformFromNode(self, node, shaderStage, type ):
        uniformNode = super().getUniformFromNode( node, shaderStage, type )
        nodeData = self.getDataFromNode( node, shaderStage )
        if nodeData.uniformGPU is None:
            uniformGPU = None
            bindings = self.bindings[ shaderStage ]
            if type == 'texture' or type == 'cubeTexture':
                sampler = WgpuNodeSampler( f'{uniformNode.name}_sampler', uniformNode.node )
                # texture = WgpuNodeSampledTexture( uniformNode.name, uniformNode.node )

                if type == 'texture':
                    texture = WgpuNodeSampledTexture( uniformNode.name, uniformNode.node )
                elif type == 'cubeTexture':
                    texture = WgpuNodeSampledCubeTexture( uniformNode.name, uniformNode.node )

                # add first textures in sequence and group for last
                lastBinding = bindings[ -1 ]
                index = len(bindings)-1 if (lastBinding and lastBinding.isUniformsGroup) else len(bindings)

                if shaderStage == 'fragment':
                    bindings[index:index] = [sampler, texture]
                    uniformGPU = [ sampler, texture ]
                else:
                    bindings[index:index] = [texture]
                    uniformGPU = [ texture ]
            
            elif type == 'buffer':
                buffer = WgpuUniformBuffer( 'NodeBuffer_' + str(node.id), node.value )

                # add first textures in sequence and group for last
                lastBinding = bindings[ - 1 ] if bindings else None
                index = len(bindings)-1 if (lastBinding and lastBinding.isUniformsGroup) else len(bindings)
                
                bindings[index:index] = [buffer]
                uniformGPU = buffer

            else:
                uniformsGroup = self.uniformsGroup.get(shaderStage, None)

                if not uniformsGroup:
                    uniformsGroup = WgpuNodeUniformsGroup( shaderStage )
                    self.uniformsGroup[ shaderStage ] = uniformsGroup
                    bindings.append( uniformsGroup )
                if node.isArrayInputNode:
                    uniformGPU = []
                    for inputNode in node.nodes:
                        uniformNodeGPU = self._getNodeUniform( inputNode, type )

                        # fit bounds to buffer
                        uniformNodeGPU.boundary = getVectorLength( uniformNodeGPU.itemSize )
                        uniformNodeGPU.itemSize = getStrideLength( uniformNodeGPU.itemSize )

                        uniformsGroup.addUniform( uniformNodeGPU )
                        uniformGPU.append( uniformNodeGPU )

                else:
                    uniformGPU = self._getNodeUniform( uniformNode, type )
                    uniformsGroup.addUniform( uniformGPU )

            nodeData.uniformGPU = uniformGPU
            if shaderStage == 'vertex':
                self.bindingsOffset[ 'fragment' ] = len(bindings)
        return uniformNode

    def isReference( self, type ):
        return super().isReference( type ) or type == 'texture_2d' or type == 'texture_cube'

    def getInstanceIndex( self, shaderStage = None ):
        if shaderStage == None:
            shaderStage = self.shaderStage

        self.builtins.add( 'instance_index' )

        if shaderStage == 'vertex':
            return 'instanceIndex'


    def getAttributes(self, shaderStage ):
        snippets = []
        if shaderStage == 'vertex':
            if 'instance_index' in self.builtins:
                snippets.append( '@builtin( instance_index ) instanceIndex : u32' )

            attributes = self.attributes
            for index, attribute in enumerate(attributes):
                name = attribute.name
                type = self.getType( attribute.type )
                snippets.append(f'@location( {index} ) { name } : { type }')

        return  ',\n\t'.join(snippets)


    def getVars( self, shaderStage ):

        snippets = []

        vars = self.vars[ shaderStage ]

        for variable in vars:
            name = variable.name
            type = self.getType( variable.type )
            snippets.append( f'\tvar {name} : {type}; ' )

        code = '\n'.join( snippets )
        return f"\n{code}\n"


    def getVarys(self, shaderStage ):
        snippets = []
        if shaderStage == 'vertex':
            snippets.append( '@builtin( position ) Vertex: vec4<f32>' )
            varys = self.varys

            for index, vary in enumerate(varys):
                snippets.append(f'@location( {index} ) { vary.name } : { self.getType( vary.type ) }' )

        elif shaderStage == 'fragment':
            varys = self.varys
            for index, vary in enumerate(varys):
                snippets.append( f'@location( {index} ) { vary.name } : { self.getType( vary.type ) }' )

        code = ',\n\t'.join(snippets)
        return self._getWGSLStruct( 'NodeVarysStruct', '\t' + code ) if shaderStage == 'vertex' else code

    
    def getUniforms(self, shaderStage ):

        uniforms = self.uniforms[ shaderStage ]

        bindingSnippets = []
        bufferSnippets = []
        groupSnippets = []

        index = self.bindingsOffset[ shaderStage ]

        for uniform in uniforms:
            if uniform.type == 'texture':
                
                if shaderStage == 'fragment':
                    bindingSnippets.append( f'@group( 0 ) @binding( {index} ) var {uniform.name}_sampler : sampler;' )
                    index += 1

                bindingSnippets.append( f'@group( 0 ) @binding( {index} ) var {uniform.name} : texture_2d<f32>;' )
                index += 1

            elif uniform.type == 'cubeTexture':

                if shaderStage == 'fragment':
                    bindingSnippets.append( f'@group( 0 ) @binding( {index} ) var {uniform.name}_sampler : sampler;' )
                    index += 1

                bindingSnippets.append( f'@group( 0 ) @binding( {index} ) var {uniform.name} : texture_cube<f32>;' )
                index += 1

            elif uniform.type == 'buffer' or uniform.type == 'storageBuffer':
                bufferNode = uniform.node
                bufferType = self.getType( bufferNode.bufferType )
                bufferCount = bufferNode.bufferCount

                bufferCountSnippet =  ', ' + str(bufferCount) if bufferCount > 0 else ''
                bufferSnippet = f'\t{uniform.name} : array< {bufferType}{bufferCountSnippet} >\n'
                bufferAccessMode = 'storage,read_write' if bufferNode.isStorageBufferNode else 'uniform'

                bufferSnippets.append( self._getWGSLStructBinding( 'NodeBuffer_' + str(bufferNode.id), bufferSnippet, bufferAccessMode, index ) )
                index += 1

            else:
                vectorType = self.getType( self.getVectorType( uniform.type ) )

                if isinstance(uniform.value, Iterable):
                    length = len(uniform.value)
                    groupSnippets.append( f'uniform {vectorType}[ {length} ] {uniform.name}' )
                else:
                    groupSnippets.append( f'\t{uniform.name} : { vectorType}' )

        code = '\n'.join(bindingSnippets)
        code += '\n'.join(bufferSnippets)

        if len(groupSnippets) > 0:
            code += self._getWGSLStructBinding( 'NodeUniforms', ',\n'.join(groupSnippets), 'uniform', index )
            index += 1
        
        return code

        # if len(groupSnippet)>0:
        #     # snippet += f'layout(set = 0, binding = {index}) uniform NodeUniforms {{ {groupSnippet} }} nodeUniforms; '
        #     snippet += self._getWGSLUniforms( 'NodeUniforms', groupSnippet, index )
        #     index += 1

        # return snippet

    
    def buildCode(self):

        shadersData = Dict({ 'fragment': {}, 'vertex': {} })
       
        for shaderStage in shadersData:
            flow = '// code\n'
            flow += f'\t{ self.flowCode[ shaderStage ] }'
            flow += '\n\t'

            flowNodes = self.flowNodes[ shaderStage ]
            mainNode = flowNodes[ - 1 ]

            for node in flowNodes:
                flowSlotData = self.getFlowData( shaderStage, node )
                slotName = node.name

                if slotName:
                    if len(flow) > 0:
                        flow += '\n'
                    flow += f'\t// FLOW -> { slotName }\n\t'

                flow += f'{ flowSlotData.code }\n\t'

                if node == mainNode:
                    flow += '// FLOW RESULT\n\t'

                    if shaderStage == 'vertex':
                        flow += 'NodeVarys.Vertex = '

                    elif shaderStage == 'fragment':
                        flow += 'return '

                    flow += f'{ flowSlotData.result };'

            stageData = shadersData[ shaderStage ]

            stageData.uniforms = self.getUniforms( shaderStage )
            stageData.attributes = self.getAttributes( shaderStage )
            stageData.varys = self.getVarys( shaderStage )
            stageData.vars = self.getVars( shaderStage )
            stageData.codes = self.getCodes( shaderStage )
            stageData.flow = flow

        if self.material is not None:
            self.vertexShader = self._getWGSLVertexCode( shadersData.vertex )
            self.fragmentShader = self._getWGSLFragmentCode( shadersData.fragment )
        else:
            # self.computeShader = self._getWGSLComputeCode( shadersData.compute, ( self.object.workgroupSize || [ 64 ] ).join( ', ' ) );
            pass

    def getMethod( self, method ):
        m = wgslPolyfill.get(method, None)
        if m is not None:
            self._include( method )

        return wgslMethods.get(method, None) or method


    def getType( self, type ):
        return wgslTypeLib[ type ] if type in wgslTypeLib else type

    def isAvailable( self, name ):
        return name in supports and supports[ name ] == True

    def _include( self, name ):
        wgslPolyfill[ name ].build( self )

    def _getNodeUniform( self, uniformNode, type ):
        if type == 'float':
            return FloatNodeUniform( uniformNode )
        if type == 'vec2':
            return Vector2NodeUniform( uniformNode )
        if type == 'vec3':
            return Vector3NodeUniform( uniformNode )
        if type == 'vec4':
            return Vector4NodeUniform( uniformNode )
        if type == 'color':
            return ColorNodeUniform( uniformNode )
        if type == 'mat3':
            return Matrix3NodeUniform( uniformNode )
        if type == 'mat4':
            return Matrix4NodeUniform( uniformNode )

        raise Exception( f'Uniform "{type}" not declared.' )

    def _getWGSLVertexCode( self, shaderData ):
        return f'''{self.getSignature()}

// uniforms
{shaderData.uniforms}

// varys
{shaderData.varys}

// codes
{shaderData.codes}

@stage( vertex )
fn main( {shaderData.attributes} ) -> NodeVarysStruct {{

	// system
	var NodeVarys: NodeVarysStruct;

	// vars
	{shaderData.vars}

	// flow
	{shaderData.flow}

	return NodeVarys;

}}
'''

    def _getWGSLFragmentCode( self, shaderData ):
        return f'''{ self.getSignature() }

// uniforms
{shaderData.uniforms}

// codes
{shaderData.codes}

@stage( fragment )
fn main( {shaderData.varys} ) -> @location( 0 ) vec4<f32> {{

	// vars
	{shaderData.vars}

	// flow
	{shaderData.flow}
}}
'''

    def _getWGSLComputeCode( self, shaderData, workgroupSize ):
        pass

    def _getWGSLStruct( self, name, vars ):
        return f'''
struct {name} {{
\n{vars}
}};'''

    def _getWGSLStructBinding( self, name, vars, access, binding = 0, group = 0 ):
        structName = name + 'Struct'
        structSnippet = self._getWGSLStruct( structName, vars )

        return f'''{structSnippet}
@binding( {binding} ) @group( {group} )
var<{access}> {name} : {structName};'''




