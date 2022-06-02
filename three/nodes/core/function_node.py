#from three.renderer.nodes import CodeNode, NodeBuilder, FunctionCallNode

from .code_node import CodeNode
from .node_builder import NodeBuilder
from .function_call_node import FunctionCallNode
import re

class FunctionNode(CodeNode):

    def __init__(self, code='') -> None:
        super().__init__(code=code)
        self.inputs = []
        self.keywords = {}

    def getNodeType( self, builder:'NodeBuilder', *args ):
        return self.getNodeFunction( builder ).type

    def getInputs( self, builder ):
        return self.getNodeFunction( builder ).inputs

    def getNodeFunction( self, builder ):
        nodeData = builder.getDataFromNode( self )

        nodeFunction = nodeData.nodeFunction

        if not nodeFunction:
            nodeFunction = builder.parser.parseFunction( self.code )
            nodeData.nodeFunction = nodeFunction

        return nodeFunction


    def call(self, parameters = None ):
        return FunctionCallNode( self, parameters or {} )


    def generate(self, builder:'NodeBuilder', output ):

        super().generate( builder )

        nodeFunction = self.getNodeFunction( builder )

        name = nodeFunction.name
        type = nodeFunction.type

        nodeCode = builder.getCodeFromNode( self, type )

        if name != '' :
            # use a custom property name
            nodeCode.name = self.name


        propertyName = builder.getPropertyName( nodeCode )

        # nodeCode.code = nodeFunction.getCode( propertyName )

        code = nodeFunction.getCode( propertyName )

        keywords = self.keywords
        keywordsProperties = keywords.keys()

        if len(keywordsProperties) > 0:
            for property in keywordsProperties:
                code = code.replace( property, keywords[property] )

                propertyRegExp = re.compile(f'\\b{property}\\b')

                nodeProperty = keywords[ property ].build( builder, 'property' )

                code = propertyRegExp.sub(nodeProperty, code)

        nodeCode.code = code

        if output == 'property':
            return propertyName
        else:
            return builder.format( '{propertyName}()', type, output )