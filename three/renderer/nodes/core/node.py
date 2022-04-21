import uuid, warnings

#from three.renderer.nodes import NodeUpdateType, NodeBuilder
from ....structure import NoneAttribute
from .constants import NodeUpdateType
from .node_builder import NodeBuilder
from .node_utils import getNodesKeys

_nodeId = 0

class Node(NoneAttribute):
    def __init__(self, nodeType = None) -> None:
        self.nodeType = nodeType
        self.updateType = NodeUpdateType.NONE
        self.uuid = uuid.uuid1()
        global _nodeId
        self.id = _nodeId
        _nodeId += 1

    def getHash(self, *args):       # ( builder )
        return self.uuid

    def getUpdateType(self, *args):  # ( builder )
        return self.updateType

    def getNodeType(self, *args):  # ( builder )s
        return self.nodeType
    
    def update(self, *args):  # ( builder )
        warnings.warn( 'Abstract function.' )


    def generate(self, *args):  # ( builder )
        warnings.warn( 'Abstract function.' )


    def analyze( self, builder:'NodeBuilder' ):
        hash = self.getHash( builder )
        sharedNode = builder.getNodeFromHash( hash )

        if sharedNode and self != sharedNode:
            return sharedNode.analyze( builder )


        nodeData = builder.getDataFromNode( self )
        nodeData.dependenciesCount = 1 if nodeData.dependenciesCount is None else nodeData.dependenciesCount + 1

        nodeKeys = getNodesKeys( self )

        for property in nodeKeys:
            self.__dict__[ property ].analyze( builder )


    def build( self, builder:'NodeBuilder', output = None ):
        hash = self.getHash( builder )
        sharedNode = builder.getNodeFromHash( hash )

        if sharedNode and self != sharedNode:
            return sharedNode.build( builder, output )

        builder.addNode( self )
        builder.addStack( self )

        isGenerateOnce = self.generate.__code__.co_argcount == 2

        snippet = None

        if isGenerateOnce:
            type = self.getNodeType( builder )
            nodeData = builder.getDataFromNode( self )
            snippet = nodeData.snippet

            if snippet == None:
                snippet = self.generate( builder ) or ''
                nodeData.snippet = snippet

            snippet = builder.format( snippet, type, output )

        else:
            snippet = self.generate( builder, output ) or ''

        builder.removeStack( self )

        return snippet

    
    def serialize( self, json ):

        # const nodeKeys = getNodesKeys( this );

        # if ( nodeKeys.length > 0 ) {

        #     const inputNodes = {};

        #     for ( const property of nodeKeys ) {

        #         inputNodes[ property ] = this[ property ].toJSON( json.meta ).uuid;

        #     }

        #     json.inputNodes = inputNodes;

        # }

        raise NotImplementedError



    def deserialize( self, json ):

        # if ( json.inputNodes !== undefined ) {

        #     const nodes = json.meta.nodes;

        #     for ( const property in json.inputNodes ) {

        #         const uuid = json.inputNodes[ property ];

        #         this[ property ] = nodes[ uuid ];

        #     }

        # }

        raise NotImplementedError