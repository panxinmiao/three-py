from .texture_node import TextureNode
from ..core.uniform_node import UniformNode
from .reflect_node import ReflectNode

class CubeTextureNode(TextureNode):

    def __init__(self, value, uvNode=None, biasNode=None) -> None:
        super().__init__(value, uvNode or ReflectNode(), biasNode)

    def getInputType(self, *args):
        return 'cubeTexture'

    def generate(self, builder, output):
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

            snippet = nodeData.snippet

            if snippet is None:
                uvSnippet = self.uvNode.build( builder, 'vec3' )
                biasNode = self.biasNode

                if biasNode:
                    biasSnippet = biasNode.build( builder, 'float' )
                    snippet = builder.getCubeTextureBias( textureProperty, uvSnippet, biasSnippet )

                else:
                    snippet = builder.getCubeTexture( textureProperty, uvSnippet )

                nodeData.snippet = snippet

            return builder.format( snippet, 'vec4', output )
