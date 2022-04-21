import warnings
from ....structure import NoneAttribute

class NodeFunction(NoneAttribute):

    def __init__( self, type, inputs, name = '', presicion = '' ) -> None:
        self.type = type
        self.inputs = inputs
        self.name = name
        self.presicion = presicion

    def getCode(self, *args ):
        warnings.warn( 'Abstract function.' )
