from .material import Material
from ..math import Vector2
from ..constants import TangentSpaceNormalMap

class MeshNormalMaterial(Material):

    def __init__(self, parameters = None) -> None:
        super().__init__()

        self.type = 'MeshNormalMaterial'

        self.bumpMap = None
        self.bumpScale = 1

        self.normalMap = None
        self.normalMapType = TangentSpaceNormalMap
        self.normalScale = Vector2( 1, 1 )

        self.displacementMap = None
        self.displacementScale = 1
        self.displacementBias = 0

        self.wireframe = False
        self.wireframeLinewidth = 1

        self.fog = False

        self.flatShading = False

        self.setValues( parameters )

    def copy( self, source: 'Material' ):

        super().copy( source )

        self.bumpMap = source.bumpMap
        self.bumpScale = source.bumpScale

        self.normalMap = source.normalMap
        self.normalMapType = source.normalMapType
        self.normalScale.copy( source.normalScale )

        self.displacementMap = source.displacementMap
        self.displacementScale = source.displacementScale
        self.displacementBias = source.displacementBias

        self.wireframe = source.wireframe
        self.wireframeLinewidth = source.wireframeLinewidth

        self.flatShading = source.flatShading

        return self

