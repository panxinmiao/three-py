from ..core import Object3D, Geometry
from ..materials import Material

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

        morphAttributes = geometry.morphAttributes
        keys = list(morphAttributes.keys())

        if len(keys) > 0:
            morphAttribute = morphAttributes[ keys[ 0 ] ]

            if morphAttribute is not None:
                self.morphTargetInfluences = []
                self.morphTargetDictionary = {}
                for m in range( len(morphAttribute) ):
                    name = morphAttribute[ m ].name or str( m )
                    self.morphTargetInfluences.append( 0 )
                    self.morphTargetDictionary[ name ] = m