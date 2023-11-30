import uuid, warnings

from three.core import EventDispatcher
from .constants import NodeUpdateType
from .node_builder import NodeBuilder
from .node_utils import getCacheKey, getNodeChildren

_nodeId = 0

class Node(EventDispatcher):

    isNode = True

    def __init__(self, nodeType = None) -> None:
        self.nodeType = nodeType
        self.updateType = NodeUpdateType.NONE
        self.updateBeforeType = NodeUpdateType.NONE
        self.uuid = uuid.uuid1()
        global _nodeId
        self.__id = _nodeId
        _nodeId += 1

    @property
    def id(self):
        return self.__id

    @property
    def type(self):
        return self.__class__.__name__
    
    def getSelf(self):
        # non-node object
        return getattr(self, 'selfNode', self)
    
    def updateReference(self):
        return self

    def isGlobal(self, *args):  # ( builder )
        return False

    def getChildren(self):
        for _, _ ,childNode in getNodeChildren( self ):
            yield childNode

    def dispose(self):
        self.dispatchEvent('dispose')

    def traverse(self, callback):
        callback( self )
        for childNode in self.getChildren():
            childNode.traverse( callback )

    def getCacheKey(self):
        return getCacheKey( self )

    def getHash(self, *args):       # ( builder )
        return str(self.uuid)

    def getUpdateType(self, *args):  # ( builder )
        return self.updateType
    
    def getUpdateBeforeType(self, *args):  # ( builder )
        return self.updateBeforeType

    def getNodeType(self, builder:'NodeBuilder', *args):
        outputNode = builder.getNodeProperties(self).outputNode
        if outputNode:
            return outputNode.getNodeType( builder )

        return self.nodeType
    
    def getShared(self, builder:'NodeBuilder'):
        hash = self.getHash(builder)
        nodeFromHash = builder.getNodeFromHash(hash)
        return nodeFromHash or self
    
    def getReference(self, builder:'NodeBuilder'):
        # deprecated
        warnings.warn('getReference is deprecated, use getShared instead.')
        return self.getShared(builder)
    
    def setup(self, builder:'NodeBuilder'):
        nodeProperties = builder.getNodeProperties(self)
        for childNode in self.getChildren():
            nodeProperties['_node' + str(childNode.id)] = childNode
        
        # return a outputNode if exists
        return None

    def construct(self, builder:'NodeBuilder'):
        # deprecated
        warnings.warn('construct is deprecated, use setup instead.')
        return self.setup(builder)

    def analyze( self, builder:'NodeBuilder' ):
        nodeData = builder.getDataFromNode(self)
        nodeData.dependenciesCount = 1 if nodeData.dependenciesCount is None else nodeData.dependenciesCount + 1

        if nodeData.dependenciesCount == 1:
            # node flow children
            nodeProperties = builder.getNodeProperties(self)
            for childNode in nodeProperties.values():
                if childNode and isinstance(childNode, Node):
                    childNode.build(builder)

    def generate(self, builder, output=None):
        outputNode = builder.getNodeProperties(self).outputNode

        if outputNode and outputNode.isNode:
            return outputNode.build(builder, output)
    
    def updateBefore(self, *args):  # ( frame )
        warnings.warn('Abstract function.')

    def update(self, *args):  # ( frame )
        warnings.warn('Abstract function.')

    def build( self, builder:'NodeBuilder', output = None ):
        refNode = self.getShared(builder)

        if self != refNode:
            return refNode.build(builder, output)

        builder.addNode( self )
        builder.addStack( self )

        '''
        expected results:
            - "setup"    -> Node
            - "analyze"      -> None
            - "generate"     -> String
        '''

        result = None
        buildStage = builder.getBuildStage()

        if buildStage == 'setup' or buildStage == 'construct':
            properties = builder.getNodeProperties(self)

            if properties.initialized != True or builder.context.tempRead == False:

                # stackNodesBeforeSetup = len(builder.stack.nodes)

                properties.initialized = True
                properties["outputNode"] = self.construct(builder)

                # if properties.outputNode and len(builder.stack.nodes) != stackNodesBeforeSetup:
                #     properties.outputNode = builder.stack

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

        # builder.removeChain( self )
        builder.removeStack(self)

        return result

    def getSerializeChildren(self):
        return getNodeChildren(self)
    
    def serialize( self, json ):
        raise NotImplementedError

    def deserialize( self, json ):
        raise NotImplementedError

_NodeClasses = {}

def addNodeClass(classType, nodeClass):
    if not issubclass(nodeClass, Node) or classType is None:
        raise Exception(f'Node class {classType} is not a class')

    if classType in _NodeClasses:
        raise Exception(f'Redefinition of node class {classType}')
    _NodeClasses[classType] = nodeClass
    nodeClass.type = classType

def createNodeFromType(classType):
    Cls = _NodeClasses.get( classType, None )
    if Cls:
        return Cls()