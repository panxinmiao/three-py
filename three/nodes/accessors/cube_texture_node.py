from three.nodes.accessors.uv_node import UVNode
from .texture_node import TextureNode
from ..core.uniform_node import UniformNode
from .reflect_node import ReflectNode

class CubeTextureNode(TextureNode):

    def __init__(self, value, uvNode=None, levelNode=None) -> None:

        super().__init__(value, uvNode, levelNode)

        # Important: We don't need auto to creat a default UvNode (auto behavior in TextureNode.__init__) for CubeTextureNode.
        self.uvNode = uvNode 

    def getInputType(self, *args):
        return 'cubeTexture'

    def getConstructHash(self, builder):
        return f"{ self.uuid } / { builder.context.environmentContext.uuid if builder.context.environmentContext else '' }"

    def construct(self, builder):
        properties = builder.getNodeProperties(self)
        uvNode = self.uvNode or builder.context.uvNode or ReflectNode()
        levelNode = self.levelNode or builder.context.levelNode

        if levelNode and levelNode.isNode:
            texture = self.value
            levelNode = builder.context.levelShaderNode(
                {'texture': texture, 'levelNode': levelNode}, builder) if builder.context.levelShaderNode else levelNode

        properties.uvNode = uvNode
        properties.levelNode = levelNode


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

            snippet = nodeData.snippet

            if snippet is None or builder.context.tempRead == False:
                uvSnippet = uvNode.build(builder, 'vec3')
                
                if levelNode:
                    levelSnippet = levelNode.build(builder, 'float')
                    snippet = builder.getCubeTextureLevel(textureProperty, uvSnippet, levelSnippet)
                
                else:
                    snippet = builder.getCubeTexture(textureProperty, uvSnippet)

                nodeData.snippet = snippet

            return builder.format( snippet, 'vec4', output )
