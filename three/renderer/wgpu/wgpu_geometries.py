from weakref import WeakKeyDictionary
from .wgpu_attributes import WgpuAttributes

class WgpuGeometries:

    def __init__( self, attributes: 'WgpuAttributes', info ) -> None:
        self.attributes = attributes
        self.info = info

        self.geometries = WeakKeyDictionary()

    def update( self, geometry ):
        
        if self.geometries.get( geometry ) is None:
            disposeCallback = self.onGeometryDispose
            
            self.geometries.setdefault( geometry, disposeCallback )
            
            self.info.memory.geometries +=1

            geometry.addEventListener( 'dispose', disposeCallback )


        geometryAttributes = geometry.attributes

        for name in geometryAttributes:
            self.attributes.update( geometryAttributes[ name ] )

        index = geometry.index
        
        if index:
            self.attributes.update( index, True )


    def onGeometryDispose( self, event ):
        geometry = event.target
        disposeCallback = self.geometries.get( geometry )

        self.geometries.pop( geometry )

        self.info.memory.geometries -=1

        geometry.removeEventListener( 'dispose', disposeCallback )

        #
        index = geometry.index
        geometryAttributes = geometry.attributes

        if index:
            self.attributes.remove( index )

        for name in geometryAttributes:
            self.attributes.remove( geometryAttributes[ name ] )
