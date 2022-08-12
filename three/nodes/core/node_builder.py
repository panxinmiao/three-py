import weakref, warnings, re

import three
from three.structure import NoneAttribute, Dict

from .constants import NodeUpdateType
from .node_attribute import NodeAttribute
from .node_code import NodeCode
from .node_uniform import NodeUniform
from .node_var import NodeVar
from .node_vary import NodeVary
from .node_keywords import NodeKeywords

defaultShaderStages = ['fragment', 'vertex']
shaderStages = [*defaultShaderStages, 'compute']
vector = ['x', 'y', 'z', 'w']

typeFromLength = {
    1: "float",
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
        self.material = object.material
        self.geometry = object.geometry
        self.renderer = renderer
        self.parser = parser

        self.nodes = []
        self.updateNodes = []
        self.hashNodes = Dict({})

        self.scene = None
        self.lightNode = None
        self.fogNode = None

        self.vertexShader = None
        self.fragmentShader = None
        self.computeShader = None

        self.flowNodes = {'vertex': [], 'fragment': [], 'compute': []}
        self.flowCode = {'vertex': '', 'fragment': '', 'compute': ''}
        self.uniforms = {'vertex': [], 'fragment': [], 'compute': [], 'index': 0}
        self.codes = {'vertex': [], 'fragment': [], 'compute': []}
        self.attributes = []
        self.varys = []
        self.vars = {'vertex': [], 'fragment': [], 'compute': []}
        self.flow = { 'code': '' }
        self.stack = []

        self.context = Dict({
            'keywords': NodeKeywords(),
            'material': object.material
        })

        self.nodesData = weakref.WeakKeyDictionary()
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
    def getConst(self, type, value ):
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


    def getType(self, type ):
        return type

    def generateMethod(self, method ):
        return method

    def getAttribute(self, name, type ):
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
        return re.fullmatch('vec\d', type) is not None

    def isMatrix(self, type ):
        return re.fullmatch('mat\d', type) is not None

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


    def getTypeFromLength(self, length ):
        return typeFromLength.get(length)


    def getTypeLength(self, type:str ):
        vecType = self.getVectorType( type )

        if vecType:
            vecNum = re.findall('vec([2-4])', vecType)
            if len(vecNum) != 0:
                return int( vecNum[ 0 ] )
            if vecType == 'float' or vecType == 'bool' or vecType == 'int' or vecType == 'uint':
                return 1
            if 'mat3' in type:
                return 9
            if 'mat4' in type:
                return 16

        return 0


    def getVectorFromMatrix(self, type:'str' ):
        return type.replace("mat", "vec")
    
    def getDataFromNode(self, node, shaderStage = None):
        if shaderStage is None:
            shaderStage = self.shaderStage

        nodeData = self.nodesData.get( node, None )

        if nodeData is None:
            nodeData = Dict({'vertex': {}, 'fragment': {}, 'compute': {}})
            self.nodesData[node] = nodeData

        return nodeData[ shaderStage ] if shaderStage is not None else nodeData

    def getNodeProperties(self, node, shaderStage=None):
        shaderStage = shaderStage or self.shaderStage

        nodeData = self.getDataFromNode(self, shaderStage)
        constructHash = node.getConstructHash(self)

        nodeData.setdefault("properties", Dict())
        nodeData.properties.setdefault( constructHash, Dict({"outputNode": None}) )

        return nodeData.properties[constructHash]


    def getUniformFromNode(self, node, shaderStage, type ):

        nodeData = self.getDataFromNode( node, shaderStage )
        nodeUniform = nodeData.uniform

        if nodeUniform is None:
            self.uniforms['index'] += 1 
            index = self.uniforms['index']

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

    def getVaryFromNode(self, node, type ):

        nodeData = self.getDataFromNode( node, None )

        nodeVary = nodeData.vary

        if nodeVary is None:
            varys = self.varys
            index = len(varys)
            nodeVary = NodeVary( 'nodeVary' + str(index), type )
            varys.append( nodeVary )
            nodeData.vary = nodeVary
        
        return nodeVary

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

    def addFlowCode(self, code ):
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

    def getVarys(self,  shaderStage):
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
        # stage 1: generate shader node
        self.setBuildStage('construct')
        for shaderStage in shaderStages:
            self.setShaderStage( shaderStage )
            flowNodes = self.flowNodes[ shaderStage ]
            for node in flowNodes:
                node.build( self )

        # stage 2: analyze nodes to possible optimization and validation
        self.setBuildStage('analyze')

        for shaderStage in shaderStages:
            self.setShaderStage(shaderStage)
            flowNodes = self.flowNodes[shaderStage]
            for node in flowNodes:
                node.build(self)

        # stage 3: pre-build vertex code used in fragment shader
        self.setBuildStage('generate')

        if self.context.vertex and self.context.vertex.isNode:
            self.flowNodeFromShaderStage( 'vertex', self.context.vertex )

        # stage 4: generate shader
        self.setBuildStage( 'generate' )

        for shaderStage in shaderStages:
            self.setShaderStage( shaderStage )
            flowNodes = self.flowNodes[ shaderStage ]
            for node in flowNodes:
                self.flowNode( node)

        self.setBuildStage( None )
        self.setShaderStage( None )

        # stage 5: build code for a specific output
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


