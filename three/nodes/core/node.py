import uuid, warnings

#from three.renderer.nodes import NodeUpdateType, NodeBuilder
from three.structure import NoneAttribute
from .constants import NodeUpdateType
from .node_builder import NodeBuilder
from .node_utils import getCacheKey

_nodeId = 0

class Node(NoneAttribute):

    isNode = True

    def __init__(self, nodeType = None) -> None:
        self.nodeType = nodeType
        self.updateType = NodeUpdateType.NONE
        self.uuid = uuid.uuid1()
        self.isNode = True
        global _nodeId
        self.id = _nodeId
        _nodeId += 1

    def getChildren(self):
        children = []
        for property in self.__dict__:
            object = self.__dict__[property]
            if isinstance(object, list):
                for child in object:
                    if child and isinstance(child, Node):
                        children.append(child)

            elif object and isinstance(object, Node):
                children.append(object)

        return children

    def getCacheKey(self):
        # needs to be verified
        return getCacheKey( self )

    def getHash(self, *args):       # ( builder )
        return str(self.uuid)

    def getUpdateType(self, *args):  # ( builder )
        return self.updateType

    def getNodeType(self, *args):  # ( builder )s
        return self.nodeType
    
    def getConstructHash(self, *args ):
        return str(self.uuid)

    def getReference(self, builder):
        hash = self.getHash(builder)
        nodeFromHash = builder.getNodeFromHash(hash)
        return nodeFromHash or self

    def construct(self, builder):
        nodeProperties = builder.getNodeProperties(self)

        for childNode in self.getChildren():
            nodeProperties['_node' + str(childNode.id)] = childNode

        # return a outputNode if exists
        return None

    def analyze( self, builder:'NodeBuilder' ):
        # refNode = self.getReference(builder)
        nodeData = builder.getDataFromNode(self)
        nodeData.dependenciesCount = 1 if nodeData.dependenciesCount is None else nodeData.dependenciesCount + 1

        if nodeData.dependenciesCount == 1:
            # node flow children
            nodeProperties = builder.getNodeProperties(self)
            for childNode in nodeProperties.values():
                if childNode and isinstance(childNode, Node):
                    childNode.build(builder)

    def generate(self, builder, output):
        outputNode = builder.getNodeProperties(self).outputNode

        if outputNode and outputNode.isNode:
            return outputNode.build(builder, output)

    def update(self, *args):  # ( builder )
        warnings.warn('Abstract function.')

    def build( self, builder:'NodeBuilder', output = None ):
        refNode = self.getReference(builder)

        if self != refNode:
            return refNode.build(builder, output)

        builder.addNode( self )
        builder.addStack( self )

        '''
        expected return:
            - "construct"    -> Node
            - "analyze"      -> null
            - "generate"     -> String
        '''

        result = None
        buildStage = builder.getBuildStage()

        if buildStage == 'construct':
            properties = builder.getNodeProperties(self)

            if properties.initialized != True or builder.context.tempRead == False:
                properties.initialized = True
                properties["outputNode"] = self.construct(builder)
                for childNode in properties.values():
                    if childNode and isinstance(childNode, Node):
                        childNode.build(builder)

        elif buildStage == 'analyze':
            self.analyze(builder)

        elif buildStage == 'generate':
            isGenerateOnce = self.generate.__code__.co_argcount == 2
            if isGenerateOnce:
                type = self.getNodeType(builder)
                nodeData = builder.getDataFromNode(self)
                result = nodeData.snippet

                if result is None:  # or builder.context.tempRead == False
                    result = self.generate(builder) or ''
                    nodeData.snippet = result
                
                result = builder.format(result, type, output)
            else:
                result = self.generate(builder, output) or ''

        builder.removeStack( self )

        return result

    
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