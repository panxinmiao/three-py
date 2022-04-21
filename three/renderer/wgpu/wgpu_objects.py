
from weakref import WeakKeyDictionary


class WgpuObjects:

    def __init__(self, geometries, info) -> None:
        
        self.geometries = geometries
        self.info = info

        self.updateMap = WeakKeyDictionary()

    def update( self, object ):
        
        geometry = object.geometry
        updateMap = self.updateMap
        frame = self.info.render.frame
        
        if not geometry.isBufferGeometry:
            raise ValueError( 'THREE.WebGPURenderer: This renderer only supports THREE.BufferGeometry for geometries.' )

        if updateMap.get( geometry ) != frame:
            self.geometries.update( geometry )
            updateMap[geometry] = frame

    def dispose(self):
        self.updateMap = WeakKeyDictionary()

