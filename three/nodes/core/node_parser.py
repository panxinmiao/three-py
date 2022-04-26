import warnings
from three.structure import NoneAttribute

class NodeParser(NoneAttribute):

    def parseFunction(self, source):
        warnings.warn( 'Abstract function.' )