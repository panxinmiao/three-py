from .material import Material
from ..math import Color
from ..constants import MultiplyOperation

class MeshBasicMaterial(Material):
    def __init__(self, parameters = {}, **kwargs) -> None:
        '''
        parameters = {
            color: <hex>,
            opacity: <float>,
            map: THREE.Texture( <Image> ),
    
            lightMap: THREE.Texture( <Image> ),
            lightMapIntensity: <float>

            aoMap: THREE.Texture( <Image> ),
            aoMapIntensity: <float>

            specularMap: THREE.Texture( <Image> ),

            alphaMap: THREE.Texture( <Image> ),

            envMap: THREE.CubeTexture( [posx, negx, posy, negy, posz, negz] ),
            combine: THREE.Multiply,
            reflectivity: <float>,
            refractionRatio: <float>,

            depthTest: <bool>,
            depthWrite: <bool>,

            wireframe: <boolean>,
            wireframeLinewidth: <float>,
        }
        '''
        super().__init__()

        self._type = 'MeshBasicMaterial'

        self.color = Color( 0xffffff )  # emissive

        self.map = None

        self.lightMap = None
        self.lightMapIntensity = 1.0

        self.aoMap = None
        self.aoMapIntensity = 1.0

        self.specularMap = None

        self.alphaMap = None

        self.envMap = None
        self.combine = MultiplyOperation
        self.reflectivity = 1
        self.refractionRatio = 0.98

        self.wireframe = False
        self.wireframeLinewidth = 1
        self.wireframeLinecap = 'round'
        self.wireframeLinejoin = 'round'

        if not isinstance(parameters, dict):
            parameters = parameters.__dict__
            
        parameters = parameters.copy()
        parameters.update(kwargs)

        self.setValues(parameters)


    def copy( self, source: 'Material' ):

        super().copy( source )

        self.color.copy( source.color )

        self.map = source.map

        self.lightMap = source.lightMap
        self.lightMapIntensity = source.lightMapIntensity

        self.aoMap = source.aoMap
        self.aoMapIntensity = source.aoMapIntensity

        self.specularMap = source.specularMap

        self.alphaMap = source.alphaMap

        self.envMap = source.envMap
        self.combine = source.combine
        self.reflectivity = source.reflectivity
        self.refractionRatio = source.refractionRatio

        self.wireframe = source.wireframe
        self.wireframeLinewidth = source.wireframeLinewidth
        self.wireframeLinecap = source.wireframeLinecap
        self.wireframeLinejoin = source.wireframeLinejoin

        return self

