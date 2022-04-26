#from three.renderer.nodes import Node, LightNode

from ..core.node import Node
from .light_node import LightNode


def sortLights( lights:'list' ):
    lights.sort(key='id')


class LightsNode(Node):

    def __init__(self, lightNodes = None) -> None:
        super().__init__('vec3')
        self.lightNodes = lightNodes or []
        self._hash = None

    @property
    def hasLight(self):
        return len(self.lightNodes) > 0


    def generate(self, builder ):

        lightNodes = self.lightNodes

        for lightNode in lightNodes:
            lightNode.build( builder )

        return 'vec3( 0.0 )'


    def getHash(self, *args ):

        if self._hash is None:

            hash = ''
            lightNodes = self.lightNodes

            for lightNode in lightNodes:

                hash += lightNode.light.uuid + ' '

            self._hash = hash

        return self._hash


    def getLightNodeByHash( self, hash ):

        lightNodes = self.lightNodes

        for lightNode in lightNodes:
            if lightNode.light.uuid == hash:

                return lightNode

        return None


    def fromLights( self, lights ):
        lightNodes = []

        for light in lights:
            lightNode = self.getLightNodeByHash( light.uuid )
            if lightNode is None:
                lightNode  = LightNode( light )
            
            lightNodes.append( lightNode )

        self.lightNodes = lightNodes
        self._hash = None

        return self