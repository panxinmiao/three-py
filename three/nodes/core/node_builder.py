import weakref, warnings, re

import three
from three.structure import NoneAttribute, Dict

from .constants import NodeUpdateType
from .node_attribute import NodeAttribute
from .node_code import NodeCode
from .node_uniform import NodeUniform
from .node_var import NodeVar
from .node_varying import NodeVarying
from .node_keywords import NodeKeywords
from .node_cache import NodeCache

defaultShaderStages = ['fragment', 'vertex']
defaultBuildStages = ['construct', 'analyze', 'generate']
shaderStages = [*defaultShaderStages, 'compute']
vector = ['x', 'y', 'z', 'w']

typeFromLength = {
    2: "vec2",
    3: "vec3",
    4: "vec4",
    9: "mat3",
    16: "mat4"
}

_componet_exp = re.compile('(b|i|u|)(vec|mat)([2-4])')

class NodeBuilder(NoneAttribute):

    def __init__(self, object, renderer, parser) -> None:
        self.object = object
        self.material:three.Material = object.material
        self.geometry:three.Geometry = object.geometry
        self.renderer = renderer
        self.parser = parser

        self.nodes = []
        self.updateNodes = []
        self.hashNodes = Dict({})

        self.scene = None
        self.lightsNode = None
        self.fogNode = None

        self.vertexShader = None
        self.fragmentShader = None
        self.computeShader = None

        self.flowNodes = {'vertex': [], 'fragment': [], 'compute': []}
        self.flowCode = {'vertex': '', 'fragment': '', 'compute': ''}
        self.uniforms = {'vertex': [], 'fragment': [], 'compute': [], 'index': 0}
        self.codes = {'vertex': [], 'fragment': [], 'compute': []}
        self.attributes = []
        self.varyings = []
        self.vars = {'vertex': [], 'fragment': [], 'compute': []}
        self.flow = { 'code': '' }
        self.stack = []

        from ..shadernode.shader_node_base_elements import mul, maxMipLevel
        self.context = Dict({
            'keywords': NodeKeywords(),
            'material': object.material,
            'getMipLevelAlgorithmNode': lambda textureNode, levelNode: mul(levelNode, maxMipLevel(textureNode))
        })

        # self.nodesData = weakref.WeakKeyDictionary()
        self.cache = NodeCache()
        self.globalCache = self.cache

        self.flowsData = weakref.WeakKeyDictionary()

        self.shaderStage = None
        self.buildStage = None

    @property
    def node(self):
        return self.stack[- 1]

    def addStack(self, node ):
        '''
        if ( this.stack.indexOf( node ) !== - 1 ) {
            console.warn( 'Recursive node: ', node );
        }
        '''
        self.stack.append( node )

    def removeStack(self, node ):
        lastStack = self.stack.pop()
        if lastStack != node:
            raise Exception( 'NodeBuilder: Invalid node stack!' )

    def setHashNode( self, node, hash ):
        self.hashNodes[ hash ] = node

    def addNode(self, node):
        if node not in self.nodes:
            updateType = node.getUpdateType( self )
            if updateType != NodeUpdateType.NONE:
                self.updateNodes.append( node )
            
            self.nodes.append( node )
            self.setHashNode( node, node.getHash( self ) )


    def getMethod(self, method ):
        return method

    def getNodeFromHash(self, hash ):
        return self.hashNodes[ hash ]

    def addFlow(self, shaderStage, node ):
        self.flowNodes[ shaderStage ].append( node )
        return node

    def setContext(self, context ):
        if not isinstance(context, Dict):
            context = Dict(context)
        self.context = context

    def getContext(self):
        return self.context
    
    def setCache(self, cache ):
        self.cache = cache
    
    def getCache(self):
        return self.cache

    def getContextValue(self, name ):
        return self.context[ name ]

    def isAvailable( self, *args ):
        return False

    def getInstanceIndex( self, *args ):
        # /*shaderStage*/
        warnings.warn( 'Abstract function.' )

    def getVertexIndex( self, *args ):
        '''/* shaderStage */'''
        warnings.warn( 'Abstract function.' )

    def getFrontFacing(self, *args):
        warnings.warn('Abstract function.')

    def getFragCoord(self, *args):
        warnings.warn( 'Abstract function.' )

    def isFlipY(self):
        return False

    def getTexture(self, *args ):
        '''/* textureProperty, uvSnippet */'''
        warnings.warn( 'Abstract function.' )

    def getTextureLevel(self, *args):
        '''/* textureProperty, uvSnippet, biasSnippet */'''
        warnings.warn( 'Abstract function.' )

    def getCubeTexture(self, *args ):
        '''textureProperty, uvSnippet'''
        warnings.warn( 'Abstract function.' )

    def getCubeTextureLevel(self, *args):
        ''' /* textureProperty, uvSnippet, biasSnippet */ '''
        warnings.warn( 'Abstract function.' )

    # rename to generateConst
    def getConst(self, type, value=None ):
        if value is None:
            if type == 'float' or type == 'int' or type == 'uint':
                value = 0
            elif type == 'bool':
                value = False
            elif type == 'color':
                value = three.Color()
            elif type == 'vec2':
                value = three.Vector2()
            elif type == 'vec3':
                value = three.Vector3()
            elif type == 'vec4':
                value = three.Vector4()

        if type == 'float':
            # return str(value) + ('' if value % 1 else '.0')
            return str(float(value))
        if type == 'int':
            return f'{ round( value ) }'
        if type == 'uint':
            return f'{ round( value ) }u' if value > 0 else '0u'
        if type == 'bool':
            return 'true' if value else 'false'
        if type == 'color':
            return f"{ self.getType( 'vec3' ) }( {float(value.r)}, {float(value.g)}, {float(value.b)} )"
        
        typeLength = self.getTypeLength( type )
        componentType = self.getComponentType( type )
        getConst = lambda value : self.getConst( componentType, value )

        if typeLength == 2:
            return f'{ self.getType( type ) }( { getConst( value.x ) }, { getConst( value.y ) } )'

        elif typeLength == 3:
            return f'{ self.getType( type ) }( { getConst( value.x ) }, { getConst( value.y ) }, { getConst( value.z ) } )'

        elif typeLength == 4:
            return f'{ self.getType( type ) }( { getConst( value.x ) }, { getConst( value.y ) }, { getConst( value.z ) }, { getConst( value.w ) } )'
        
        elif typeLength > 4:
            return f'{ self.getType( type ) }()'

        raise Exception(f"NodeBuilder: Type '{type}' not found in generate constant attempt." )


    def getType(self, type):
        return type

    def generateMethod(self, method):
        return method

    def hasGeometryAttribute(self, name):
        if self.geometry is None:
            return False
        return self.geometry.hasAttribute(name)

    def getAttribute(self, name, type):
        attributes = self.attributes

        #find attribute
        for attribute in attributes:
            if attribute.name == name:
                return attribute

        #create a new if no exist
        attribute = NodeAttribute( name, type )
        attributes.append( attribute )

        return attribute

    def getPropertyName(self, node, *args):
        '''/*, shaderStage*/'''
        return node.name

    def isVector(self, type ):
        # return re.fullmatch('vec\d', type) is not None
        return type.startswith('vec')

    def isMatrix(self, type ):
        # return re.fullmatch('mat\d', type) is not None
        return type.startswith('mat')

    def isReference( self, type ):
        return type == 'void' or type == 'property' or type == 'sampler' or type == 'texture' or type == 'cubeTexture'

    def isShaderStage(self, shaderStage ):
        return self.shaderStage == shaderStage

    def getTextureEncodingFromMap(self, map ):
        encoding = None
        if map and map.isTexture:
            encoding = map.encoding

        elif map and map.isRenderTarget:
            encoding = map.texture.encoding
        else:
            encoding = three.LinearEncoding

        return encoding

    def getComponentType( self, type ):
        type = self.getVectorType( type )

        if type == 'float' or type == 'bool' or type == 'int' or type == 'uint':
            return type
        
        match = _componet_exp.match(type)
        if match is None:
            return None

        componentType = match.groups()
        if componentType[ 0 ] == 'b':
            return 'bool'
        if componentType[ 0 ] == 'i':
            return 'int'
        if componentType[ 0 ] == 'u':
            return 'uint'

        return 'float'

    def getVectorType( self, type ):
        if type == 'color':
            return 'vec3'
        if type == 'texture':
            return 'vec4'
        
        return type


    def getTypeFromLength(self, length, componentType='float'):
        if length == 1:
            return componentType
        baseType = typeFromLength.get( length )
        prefix = '' if componentType == 'float' else componentType[ 0 ]
        return prefix + baseType


    def getTypeLength(self, type:str ):
        vecType = self.getVectorType( type )

        if vecType:
            # vecNum = re.findall('vec([2-4])', vecType)
            # if len(vecNum) != 0:
            #     return int( vecNum[ 0 ] )
            if 'vec2' in vecType:
                return 2
            if 'vec3' in vecType:
                return 3
            if 'vec4' in vecType:
                return 4
            if vecType == 'float' or vecType == 'bool' or vecType == 'int' or vecType == 'uint':
                return 1
            if 'mat3' in type:
                return 9
            if 'mat4' in type:
                return 16

        return 0


    def getVectorFromMatrix(self, type:'str'):
        return type.replace("mat", "vec")

    def changeComponentType(self, type, newComponentType):
        typeLength = self.getTypeLength( type )
        return self.getTypeFromLength(typeLength, newComponentType)
    
    def getIntegerType(self, type):
        componentType = self.getComponentType(type)
        if componentType == 'int' or componentType == 'uint':
            return type
        return self.changeComponentType(type, 'int')
    
    def getDataFromNode(self, node, shaderStage = None):
        if shaderStage is None:
            shaderStage = self.shaderStage

        cache = self.globalCache if node.isGlobal(self) else self.cache
        nodeData = cache.getNodeData( node )

        if nodeData is None:
            nodeData = Dict({'vertex': {}, 'fragment': {}, 'compute': {}})
            cache.setNodeData( node, nodeData )

        return nodeData[ shaderStage ] if shaderStage is not None else nodeData

    def getNodeProperties(self, node, shaderStage=None):
        shaderStage = shaderStage or self.shaderStage

        nodeData = self.getDataFromNode( node, shaderStage )

        nodeData.setdefault("properties", Dict({"outputNode": None}))

        return nodeData.properties


    def getUniformFromNode(self, node, shaderStage, type ):

        nodeData = self.getDataFromNode( node, shaderStage )
        nodeUniform = nodeData.uniform

        if nodeUniform is None:
            index = self.uniforms['index']
            self.uniforms['index'] += 1 

            nodeUniform = NodeUniform( 'nodeUniform' + str(index), type, node )
            self.uniforms[ shaderStage ].append( nodeUniform )
            nodeData.uniform = nodeUniform
        
        return nodeUniform

    def getVarFromNode(self, node, type, shaderStage = None):
        if shaderStage is None:
            shaderStage = self.shaderStage

        nodeData = self.getDataFromNode( node, shaderStage )

        nodeVar = nodeData.variable

        if nodeVar is None:
            vars = self.vars[ shaderStage ]
            index = len(vars)
            nodeVar = NodeVar( 'nodeVar' + str(index), type )
            vars.append( nodeVar )
            nodeData.variable = nodeVar

        return nodeVar

    def getVaryingFromNode(self, node, type ):

        nodeData = self.getDataFromNode( node, None )

        nodeVarying = nodeData.varying

        if nodeVarying is None:
            varyings = self.varyings
            index = len(varyings)
            nodeVarying = NodeVarying( 'nodeVarying' + str(index), type )
            varyings.append( nodeVarying )
            nodeData.varying = nodeVarying
        
        return nodeVarying

    def getCodeFromNode(self, node, type, shaderStage = None):
        if shaderStage is None:
            shaderStage = self.shaderStage

        nodeData = self.getDataFromNode( node )
        nodeCode = nodeData.code

        if nodeCode is None:
            codes = self.codes[ shaderStage ]
            index = len(codes)
            nodeCode = NodeCode( 'nodeCode' + str(index), type )
            codes.append( nodeCode )
            nodeData.code = nodeCode

        return nodeCode

    def addFlowCode(self, code:str, breakline = True ):
        # _flow_p = re.compile(r'.*;\s*$')
        if breakline and not code.rstrip().endswith(';'):
            code += ';\n\t'
        self.flow.code += code

    def getFlowData(self, node, *args):
        return self.flowsData.get( node )

    def flowNode( self, node, *args ):
        output = node.getNodeType( self )
        flowData = self.flowChildNode( node, output )
        self.flowsData[node] = flowData

        return flowData

    def flowChildNode(self, node, output = None ):

        previousFlow = self.flow

        flow = Dict({
            'code': '',
        })

        self.flow = flow

        flow['result'] = node.build( self, output )

        self.flow = previousFlow

        return flow

    def flowNodeFromShaderStage(self, shaderStage, node, output = None, propertyName = None ):
        previousShaderStage = self.shaderStage
        self.setShaderStage( shaderStage )
        flowData = self.flowChildNode( node, output )

        if propertyName is not None:
            flowData.code += f'{propertyName} = {flowData.result};\n\t'
        
        self.flowCode[ shaderStage ] = self.flowCode[ shaderStage ] + flowData.code

        self.setShaderStage( previousShaderStage )

        return flowData

    def getAttributes(self, shaderStage ):
        warnings.warn( 'Abstract function.' )

    def getVaryings(self,  shaderStage):
        warnings.warn( 'Abstract function.' )


    def getVars(self, shaderStage ):
        snippet = ''
        vars = self.vars[ shaderStage ]
        for variable in vars:
            snippet += f'{variable.type} {variable.name}; '

        return snippet

    def getUniforms(self, shaderStage):
        warnings.warn( 'Abstract function.' )


    def getCodes(self, shaderStage ):
        codes = self.codes[ shaderStage ]
        code = ''

        for nodeCode in codes:
            code += nodeCode.code + '\n'

        return code

    def getHash( self ):
        return self.vertexShader + self.fragmentShader + self.computeShader

    def setShaderStage(self, shaderStage):
        self.shaderStage = shaderStage

    def getShaderStage( self ):
        return self.shaderStage

    def setBuildStage(self, buildStage):
        self.buildStage = buildStage

    def getBuildStage(self):
        return self.buildStage

    def buildCode(self):
        warnings.warn( 'Abstract function.' )


    def build(self):
        
        # construct() -> stage 1: create possible new nodes and returns an output reference node
        # analyze()   -> stage 2: analyze nodes to possible optimization and validation
        # generate()  -> stage 3: generate shader

        for buildStage in defaultBuildStages:
            self.setBuildStage( buildStage )
            if self.context.vertex and self.context.vertex.isNode:
                self.flowNodeFromShaderStage( 'vertex', self.context.vertex )

            for shaderStage in shaderStages:
                self.setShaderStage( shaderStage )
                flowNodes = self.flowNodes[ shaderStage ]
                for node in flowNodes:
                    if buildStage == 'generate':
                        self.flowNode( node )
                    else:
                        node.build( self )
        
        self.setBuildStage( None )
        self.setShaderStage( None )

        # stage 4: build code for a specific output
        self.buildCode()

        return self


    def format(self, snippet, fromType, toType ):
        fromType = self.getVectorType( fromType )
        toType = self.getVectorType( toType )

        if fromType == toType or toType is None or self.isReference( toType ):
            return snippet

        fromTypeLength = self.getTypeLength( fromType )
        toTypeLength = self.getTypeLength( toType )
        if fromTypeLength > 4: # fromType is matrix-like

            # ignore for now
            return snippet

        if toTypeLength > 4 or toTypeLength == 0: # toType is matrix-like or unknown
            # ignore for now
            #return `${ this.getType( toType ) }( ${ snippet } )`;
            return snippet

        if fromTypeLength == toTypeLength:
            return f'{ self.getType( toType ) }( { snippet } )'

        if fromTypeLength > toTypeLength:
            return self.format( f"{ snippet }.{ 'xyz'[:toTypeLength] }", self.getTypeFromLength( toTypeLength ), toType )

        if toTypeLength == 4: # toType is vec4-like
            return f"{ self.getType( toType ) }( { self.format( snippet, fromType, 'vec3' ) }, 1.0 )"

        if fromTypeLength == 2:  # fromType is vec2-like and toType is vec3-like
            return f"{ self.getType( toType ) }( { self.format( snippet, fromType, 'vec2' ) }, 0.0 )"

        return f"{ self.getType( toType ) }( { snippet } )" # fromType is float-like

    def getSignature(self):
        return f'// Three r{ three.__version__ } - NodeMaterial System\n'


