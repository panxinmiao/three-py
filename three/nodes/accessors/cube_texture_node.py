from .texture_node import TextureNode
from ..core.uniform_node import UniformNode
from .reflect_vector_node import ReflectVectorNode
from ..shadernode.shader_node_base_elements import negate, vec3, nodeObject

class CubeTextureNode(TextureNode):

    isCubeTextureNode = True

    defaultUV = None

    def __init__(self, value, uvNode=None, levelNode=None) -> None:

        super().__init__(value, uvNode, levelNode)


    def getInputType(self, *args):
        return 'cubeTexture'
    
    def getDefaultUV(self):
        CubeTextureNode.defaultUV = CubeTextureNode.defaultUV or ReflectVectorNode()
        return CubeTextureNode.defaultUV

    def generate(self, builder, output):
        properties = builder.getNodeProperties(self)
        uvNode = properties.uvNode
        levelNode = properties.levelNode
        texture = self.value

        if not texture or texture.isCubeTexture != True:
            raise Exception('CubeTextureNode: value must be a CubeTexture')

        textureProperty = UniformNode.generate(self, builder, 'cubeTexture')

        if output == 'sampler':
            return textureProperty + '_sampler'

        elif builder.isReference( output ):
            return textureProperty
            
        else:
            nodeData = builder.getDataFromNode( self )

            propertyName = nodeData.propertyName

            if propertyName is None:

                uvNodeObject = nodeObject( uvNode )
                cubeUV = vec3( negate( uvNodeObject.x ), uvNodeObject.yz)
                uvSnippet = cubeUV.build( builder, 'vec3' )

                nodeVar = builder.getVarFromNode( self, 'vec4' )

                propertyName = builder.getPropertyName( nodeVar)

                snippet = None
                
                if levelNode and levelNode.isNode:
                    levelSnippet = levelNode.build(builder, 'float')
                    snippet = builder.getCubeTextureLevel(textureProperty, uvSnippet, levelSnippet)
                
                else:
                    snippet = builder.getCubeTexture(textureProperty, uvSnippet)

                builder.addFlowCode(f'{propertyName} = {snippet}')

                nodeData.snippet = snippet
                nodeData.propertyName = propertyName

            return builder.format( propertyName, 'vec4', output )
