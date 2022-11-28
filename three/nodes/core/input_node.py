#from three.renderer.nodes import Node
from .node import Node
from warnings import warn
from .node_utils import getValueType, getValueFromType

class InputNode(Node):

    isInputNode = True

    def __init__(self, value, nodeType = None ) -> None:
        super().__init__(nodeType)
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value is None:
            warn('InputNode.value should be not None.')
            value = 0
        self._value = value

    def getNodeType( self, *args):  #  /*builder*/
        if self.nodeType is None:
            return getValueType( self.value )
        return self.nodeType

    def getInputType( self, builder ):
        return self.getNodeType( builder )


    def serialize(self, data ):
        super().serialize( data )
        if self.value and hasattr(self.value, 'toArray'):
            data.value = self.value.toArray()
        else:
            data.value = self.value

        data.valueType = getValueType( self.value )
        data.nodeType = self.nodeType


    def deserialize( self, data ):
        super().deserialize( data )

        self.nodeType = data.nodeType
        self.value = getValueFromType( data.valueType )

        if self.value and hasattr(self.value, 'fromArray'):
            self.value = self.value.fromArray( data.value )
        else:
            self.value = data.value


    def generate( self, *args ):  # builder, output
        warn('Abstract function.')
