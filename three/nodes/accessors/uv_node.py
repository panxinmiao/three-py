
from ..core.attribute_node import AttributeNode

class UVNode(AttributeNode):

    def __init__(self, index=0) -> None:
        super().__init__(None, 'vec2')
        self.index = index

    def getAttributeName(self, *args ):
        index = self.index
        return 'uv' + ( (index + 1) if index > 0 else '' )

    def serialize( self, data ):
        super().serialize( data )
        data.index = self.index

    def deserialize( self, data ):
        super().deserialize( data )
        self.index = data.index