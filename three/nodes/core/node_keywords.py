from three.structure import NoneAttribute
import re

class NodeKeywords(NoneAttribute):

    def __init__(self) -> None:
        self.keywords = []
        self.nodes = {}
        self.keywordsCallback = {}

    def getNode( self, name ):
        node = self.nodes.get(name, None)

        if node is None and name in self.keywordsCallback:

            node = self.keywordsCallback[ name ]( name )

            self.nodes[ name ] = node

        return node


    def addKeyword( self, name, callback ):
        self.keywords.append( name )
        self.keywordsCallback[ name ] = callback
        return self


    def parse( self, code ):
        keywordNames = self.keywords

        s = "\\b"+'\\b|\\b'.join(keywordNames)+"\\b"
        #pattern = re.compile(f"\b{'\b|\b'.join(keywordNames)}\b")

        pattern = re.compile(s)

        codeKeywords = pattern.findall(code)
        keywordNodes = []

        if codeKeywords:
            for keyword in codeKeywords:
                node = self.getNode( keyword )
                if node and node not in keywordNodes: 
                    keywordNodes.append( node )


        return keywordNodes

    def include( self, builder, code ):
        keywordNodes = self.parse( code )
        for keywordNode in keywordNodes:
            keywordNode.build( builder )
