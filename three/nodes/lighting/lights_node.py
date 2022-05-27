#from three.renderer.nodes import Node, LightNode
from weakref import WeakKeyDictionary
from ..core.node import Node
from .lighting_node import LightingNode

references = WeakKeyDictionary()

def sortLights( lights:'list' ):
    lights.sort(key=lambda light: light.id)
    return lights


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


    def getHash(self, builder, *args ):

        if self._hash is None:

            hash = ''
            lightNodes = self.lightNodes

            for lightNode in lightNodes:

                hash += lightNode.getHash(builder) + ' '

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

        lights = sortLights(lights)

        for light in lights:
            lightNode = self.getLightNodeByHash( light.uuid )
            if lightNode is None:
                lightClass = light.__class__
                lightNodeClass = references.get(lightClass, LightingNode)
 
                lightNode = lightNodeClass(light)
            
            lightNodes.append( lightNode )

        self.lightNodes = lightNodes
        self._hash = None

        return self


    @staticmethod
    def setReference(lightClass, lightNodeClass):
        references[lightClass] = lightNodeClass

