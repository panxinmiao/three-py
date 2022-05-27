
import time
from weakref import WeakKeyDictionary
from three.structure import NoneAttribute
#from three.renderer.nodes import NodeUpdateType
from .constants import NodeUpdateType

class NodeFrame(NoneAttribute):

    def __init__(self) -> None:
        self.time = 0
        self.deltaTime = 0

        self.frameId = 0

        self.startTime = None

        self.updateMap = WeakKeyDictionary()

        self.renderer = None
        self.material = None
        self.camera = None
        self.object = None

    
    def updateNode( self, node ):
        if node.updateType == NodeUpdateType.Frame:
            if self.updateMap.get( node ) != self.frameId:
                self.updateMap[node] = self.frameId
                node.update( self )

        elif node.updateType == NodeUpdateType.Object:
            node.update( self )


    def update(self):
        self.frameId += 1

        if self.lastTime is None:
            self.lastTime = time.time()
        
        self.deltaTime = time.time() - self.lastTime

        self.lastTime = time.time()

        self.time += self.deltaTime
