
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

        # "_needsUpdate" is a flag that to force update geometry.
        # since geometry maybe a shared resource in different object, we usually need to update it only once per frame.
        # but in some cases, different objects may need to update it separately. 
        # (in RangeNode for example, geometry attribute maybe added by different objects)
        # See: RangeNode
        # TODO: remove this flag, and use a more elegant way to update geometry.
        forceUpdate = geometry._needsUpdate
        if forceUpdate or self.geometries.has(geometry) == False or updateMap.get( geometry ) != frame:
            if forceUpdate:
                geometry._needsUpdate = False
            
            material = object.material
            self.geometries.update( geometry, material.wireframe == True )
            updateMap[geometry] = frame

    def dispose(self):
        self.updateMap = WeakKeyDictionary()

