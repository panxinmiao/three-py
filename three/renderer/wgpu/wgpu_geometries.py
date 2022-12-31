from weakref import WeakKeyDictionary
from .wgpu_attributes import WgpuAttributes
from ...core.buffer_attribute import Uint32BufferAttribute, Uint16BufferAttribute

def arrayNeedsUint32( array ):
    # assumes larger values usually on last

    for i in array:
        if i >= 65535:
            return True # account for PRIMITIVE_RESTART_FIXED_INDEX, #24565
    return False

class WgpuGeometries:

    def __init__( self, attributes: 'WgpuAttributes', info ) -> None:
        self.attributes = attributes
        self.info = info

        self.geometries = WeakKeyDictionary()
        self.wireframeGeometries = WeakKeyDictionary()

    def has( self, geometry ):
        return self.geometries.get( geometry ) is not None

    def update( self, geometry, wireframe = False ):
        
        if self.geometries.get( geometry, None ) is None:
            disposeCallback = self.onGeometryDispose
            
            self.geometries[geometry] = disposeCallback
            
            self.info.memory.geometries +=1

            geometry.addEventListener( 'dispose', disposeCallback )


        geometryAttributes = geometry.attributes

        for name in geometryAttributes:
            self.attributes.update( geometryAttributes[ name ] )

        # index = geometry.index
        index = self.getIndex( geometry, wireframe )
        
        if index:
            self.attributes.update( index, True )

    
    def getIndex( self, geometry, wireframe=False ):

        index = geometry.index

        if wireframe:
            wireframeGeometries = self.wireframeGeometries
            wireframeAttribute = wireframeGeometries.get( geometry, None)
            if wireframeAttribute is None:
                wireframeAttribute = self.getWireframeIndex( geometry )
                wireframeGeometries[geometry] = wireframeAttribute
            elif wireframeAttribute.version != self.getWireframeVersion( geometry ):
                self.attributes.remove( wireframeAttribute )
                wireframeAttribute = self.getWireframeIndex( geometry )
                wireframeGeometries[geometry] = wireframeAttribute
            
            index = wireframeAttribute
        
        return index

    
    def getWireframeIndex(self, geometry ):
        indices = []

        geometryIndex = geometry.index
        geometryPosition = geometry.attributes.position

        if geometryIndex is not None:
            array = geometryIndex.array
            for i in range(0, array.length, 3):
                a = array[i]
                b = array[i+1]
                c = array[i+2]

                indices.extend([a, b, b, c, c, a])
            
        else:
            array = geometryPosition.array

            for i in range(0, len(array)//3-1, 3):
                a = i
                b = i+1
                c = i+2

                indices.extend([a, b, b, c, c, a])

        attribute = (Uint32BufferAttribute if arrayNeedsUint32( indices ) else Uint16BufferAttribute)( indices, 1 )
        attribute.version = self.getWireframeVersion( geometry )

        return attribute

    
    def getWireframeVersion(self, geometry ):
        return geometry.index.version if geometry.index is not None else geometry.attributes.position.version


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
