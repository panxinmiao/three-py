from .material import Material
from ..math import Color, Vector2
from ..constants import TangentSpaceNormalMap

class MeshStandardMaterial(Material):

    def __init__(self, parameters = None) -> None:

        '''
        parameters = {
            color: <hex>,
            roughness: <float>,
            metalness: <float>,
            opacity: <float>,

            map: THREE.Texture( <Image> ),

            lightMap: THREE.Texture( <Image> ),
            lightMapIntensity: <float>

            aoMap: THREE.Texture( <Image> ),
            aoMapIntensity: <float>

            emissive: <hex>,
            emissiveIntensity: <float>
            emissiveMap: THREE.Texture( <Image> ),

            bumpMap: THREE.Texture( <Image> ),
            bumpScale: <float>,

            normalMap: THREE.Texture( <Image> ),
            normalMapType: THREE.TangentSpaceNormalMap,
            normalScale: <Vector2>,

            displacementMap: THREE.Texture( <Image> ),
            displacementScale: <float>,
            displacementBias: <float>,

            roughnessMap: THREE.Texture( <Image> ),

            metalnessMap: THREE.Texture( <Image> ),

            alphaMap: THREE.Texture( <Image> ),

            envMap: THREE.CubeTexture( [posx, negx, posy, negy, posz, negz] ),
            envMapIntensity: <float>

            refractionRatio: <float>,

            wireframe: <boolean>,
            wireframeLinewidth: <float>,

            flatShading: <bool>
        }
        '''

        super().__init__()

        self.defines = { 'STANDARD': '' }

        self.type = 'MeshStandardMaterial'

        self.color = Color( 0xffffff ) # diffuse
        self.roughness = 1.0
        self.metalness = 0.0

        self.map = None

        self.lightMap = None
        self.lightMapIntensity = 1.0

        self.aoMap = None
        self.aoMapIntensity = 1.0

        self.emissive = Color( 0x000000 )
        self.emissiveIntensity = 1.0
        self.emissiveMap = None

        self.bumpMap = None
        self.bumpScale = 1

        self.normalMap = None
        self.normalMapType = TangentSpaceNormalMap
        self.normalScale = Vector2( 1, 1 )

        self.displacementMap = None
        self.displacementScale = 1
        self.displacementBias = 0

        self.roughnessMap = None

        self.metalnessMap = None

        self.alphaMap = None

        self.envMap = None
        self.envMapIntensity = 1.0

        self.refractionRatio = 0.98

        self.wireframe = False
        self.wireframeLinewidth = 1
        self.wireframeLinecap = 'round'
        self.wireframeLinejoin = 'round'

        self.flatShading = False

        self.setValues( parameters )

    def copy( self, source: 'Material'):

        super().copy( source )

        self.defines = { 'STANDARD': '' }

        self.color.copy( source.color )
        self.roughness = source.roughness
        self.metalness = source.metalness

        self.map = source.map

        self.lightMap = source.lightMap
        self.lightMapIntensity = source.lightMapIntensity

        self.aoMap = source.aoMap
        self.aoMapIntensity = source.aoMapIntensity

        self.emissive.copy( source.emissive )
        self.emissiveMap = source.emissiveMap
        self.emissiveIntensity = source.emissiveIntensity

        self.bumpMap = source.bumpMap
        self.bumpScale = source.bumpScale

        self.normalMap = source.normalMap
        self.normalMapType = source.normalMapType
        self.normalScale.copy( source.normalScale )

        self.displacementMap = source.displacementMap
        self.displacementScale = source.displacementScale
        self.displacementBias = source.displacementBias

        self.roughnessMap = source.roughnessMap

        self.metalnessMap = source.metalnessMap

        self.alphaMap = source.alphaMap

        self.envMap = source.envMap
        self.envMapIntensity = source.envMapIntensity

        self.refractionRatio = source.refractionRatio

        self.wireframe = source.wireframe
        self.wireframeLinewidth = source.wireframeLinewidth
        self.wireframeLinecap = source.wireframeLinecap
        self.wireframeLinejoin = source.wireframeLinejoin

        self.flatShading = source.flatShading

        return self