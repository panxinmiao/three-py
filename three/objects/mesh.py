from ..core import Object3D, Geometry
from ..materials import Material
from warnings import warn

class Mesh(Object3D):

    isMesh = True
    
    def __init__( self, geometry = None, material = None ) -> None:
        super().__init__()
        self._type = 'Mesh'
        self.geometry = geometry or Geometry()
        self.material = material or Material()

        self.updateMorphTargets()

    def copy( self, source ):
        super().copy( source )
        if source.morphTargetInfluences is not None:
            self.morphTargetInfluences = source.morphTargetInfluences.copy()

        if source.morphTargetDictionary is not None:
            self.morphTargetDictionary = source.morphTargetDictionary.copy()

        self.material = source.material
        self.geometry = source.geometry

        return self

    def updateMorphTargets(self):
        geometry = self.geometry

        if geometry.isBufferGeometry:
            morphAttributes = geometry.morphAttributes
            keys = morphAttributes.keys()

            if len(keys) > 0:
                morphTargets:list = self.morphTargetInfluences
                morphTargets = morphTargets[: len( keys )]

                for i, key in enumerate( keys ):
                    morphTargets[ i ] = 0

                self.morphTargetDictionary = morphAttributes

            if len(keys) > 0:
                morphAttribute = morphAttributes[ keys[ 0 ] ]

                if morphAttribute is not None:
                    self.morphTargetInfluences = []
                    self.morphTargetDictionary = {}
                    for m in range( morphAttribute.length ):
                        name = morphAttribute[ m ].name or str( m )
                        self.morphTargetInfluences.append( 0 )
                        self.morphTargetDictionary[ name ] = m

        else:
            morphTargets = geometry.morphTargets
            if morphTargets and len(morphTargets) > 0:
                warn( 'THREE.Mesh.updateMorphTargets() no longer supports THREE.Geometry. Use THREE.BufferGeometry instead.' )
