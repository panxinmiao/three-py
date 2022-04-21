
from ..core.node_parser import NodeParser
from .wgsl_node_function import WGSLNodeFunction

class WGSLNodeParser(NodeParser):
    def parseFunction( self, source ):
        return WGSLNodeFunction( source )