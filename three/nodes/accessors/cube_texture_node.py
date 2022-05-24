from .texture_node import TextureNode
from ..core.uniform_node import UniformNode
from .reflect_node import ReflectNode

class CubeTextureNode(TextureNode):

    def __init__(self, value, uvNode=None, levelNode=None) -> None:
        super().__init__(value, uvNode or ReflectNode(), levelNode)

    def getInputType(self, *args):
        return 'cubeTexture'

    def generate(self, builder, output):
        texture = self.value
        uvNode = self.uvNode or builder.context.uvNode or ReflectNode()

        if not texture or texture.isCubeTexture != True:
            raise Exception('CubeTextureNode: value must be a CubeTexture')

        textureProperty = UniformNode.generate(self, builder, 'cubeTexture')

        if output == 'sampler':
            return textureProperty + '_sampler'

        elif builder.isReference( output ):
            return textureProperty
            
        else:
            nodeData = builder.getDataFromNode( self )

            snippet = nodeData.snippet

            if builder.context.tempRead == False or snippet is None:
                uvSnippet = uvNode.build(builder, 'vec3')
                levelNode = self.levelNode or builder.context.levelNode

                if levelNode and levelNode.isNode:
                    levelOutNode = builder.context.levelShaderNode(
                        {'texture': texture, 'levelNode': levelNode}, builder) if builder.context.levelShaderNode else levelNode

                    levelSnippet = levelOutNode.build(builder, 'float')

                    snippet = builder.getCubeTextureLevel(textureProperty, uvSnippet, levelSnippet)
                
                else:
                    snippet = builder.getCubeTexture(textureProperty, uvSnippet)

                nodeData.snippet = snippet

            return builder.format( snippet, 'vec4', output )
