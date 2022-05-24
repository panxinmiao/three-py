from weakref import WeakKeyDictionary

class WebGPURenderState:

    def __init__(self) -> None:
        from three.nodes.lighting.lights_node import LightsNode
        self.lightsNode = LightsNode()
        self.lightsArray = []

    def init(self):
        self.lightsArray.clear()

    
    def pushLight( self, light ):
        self.lightsArray.append( light )


    def getLightsNode(self):
        return self.lightsNode.fromLights( self.lightsArray )

class WebGPURenderStates:

    def __init__(self) -> None:
        self.renderStates =  WeakKeyDictionary()

    def get(self, scene, camera):
        renderStates = self.renderStates

        renderState = renderStates.get( scene )

        if renderState is None:
            renderState =  WebGPURenderState()
            renderStates[scene] = renderState

        return renderState

    def dispose(self):
        self.renderStates = WeakKeyDictionary()