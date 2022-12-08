from ..core.uniform_node import UniformNode
from .uv_node import UVNode

class TextureNode(UniformNode):

    isTextureNode = True

    defaultUV = None

    def __init__(self, value, uvNode=None, levelNode=None) -> None:
        super().__init__(value, 'vec4')
        self.uvNode = uvNode
        self.levelNode = levelNode

    def getUniformHash( self, *args): #  /*builder*/ 
        return self.value.uuid

    def getInputType( self, *args): #  /*builder*/ 
        return 'texture'

    def getDefaultUV(self):
        TextureNode.defaultUV = TextureNode.defaultUV or UVNode()
        return TextureNode.defaultUV

    def construct(self, builder):
        properties = builder.getNodeProperties(self)

        uvNode = self.uvNode
        if uvNode is None and builder.context.getUVNode:
            uvNode = builder.context.getUVNode(self)
        
        uvNode = uvNode or self.getDefaultUV()

        levelNode = self.levelNode

        if levelNode is None and builder.context.getSamplerLevelNode:
            levelNode = builder.context.getSamplerLevelNode(self)

        properties.uvNode = uvNode
        properties.levelNode = builder.context.getMipLevelAlgorithmNode(self, levelNode) if levelNode else None

    def generate( self, builder, output ):
        properties = builder.getNodeProperties(self)
        uvNode = properties.uvNode
        levelNode = properties.levelNode
        texture = self.value

        if texture is None or texture.isTexture != True:
            raise Exception( 'TextureNode: Need a three texture.' )
        
        textureProperty = super().generate( builder, 'texture' )

        if output == 'sampler':
            return textureProperty + '_sampler'
        elif builder.isReference( output ):
            return textureProperty
        else:
            nodeData = builder.getDataFromNode( self )
            propertyName = nodeData.propertyName

            if propertyName is None:
                uvSnippet = uvNode.build( builder, 'vec2' )
                nodeVar = builder.getVarFromNode( self, 'vec4' )
                propertyName = builder.getPropertyName( nodeVar )

                if levelNode and levelNode.isNode:
                    levelSnippet = levelNode.build(builder, 'float')
                    snippet = builder.getTextureLevel( textureProperty, uvSnippet, levelSnippet )
                else:
                    snippet = builder.getTexture( textureProperty, uvSnippet )

                builder.addFlowCode(f'{propertyName} = {snippet}')

                nodeData.snippet = snippet
                nodeData.propertyName = propertyName
            return builder.format( propertyName, 'vec4', output )


    def serialize( self, data ):
        super().serialize( data )
        #data.value = self.value.toJSON( data.meta ).uuid

    def deserialize( self, data ):
        super().deserialize( data )
        #self.value = data.meta.textures[ data.value ]