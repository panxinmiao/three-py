
from ..core.node_parser import NodeParser
from .glsl_node_function import GLSLNodeFunction

class GLSLNodeParser(NodeParser):
    def parseFunction( self, source ):
        return GLSLNodeFunction( source )