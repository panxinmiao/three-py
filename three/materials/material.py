
import uuid, warnings

from ..core import EventDispatcher

from ..constants import NormalBlending, FrontSide, RGBAFormat, SrcAlphaFactor, OneMinusSrcAlphaFactor
from ..constants import AddEquation, LessEqualDepth, AlwaysStencilFunc, KeepStencilOp, FlatShading
from ..math import Color, Vector3

_material_id = 0

class Material(EventDispatcher):
    def __init__(self) -> None:
        global _material_id
        _material_id += 1
        self.id = _material_id
        self.uuid = uuid.uuid1()

        self.name = ''
        self._type= 'Material'

        self.fog = True

        self.blending = NormalBlending
        self.side = FrontSide
        self.vertexColors = False

        self.opacity = 1
        self.fromat = RGBAFormat
        self.transparent = False

        self.blendSrc = SrcAlphaFactor
        self.blendDst = OneMinusSrcAlphaFactor
        self.blendEquation = AddEquation
        self.blendSrcAlpha = None
        self.blendDstAlpha = None
        self.blendEquationAlpha = None

        self.depthFunc = LessEqualDepth
        self.depthTest = True
        self.depthWrite = True

        self.stencilWriteMask = 0xff
        self.stencilFunc = AlwaysStencilFunc
        self.stencilRef = 0
        self.stencilFuncMask = 0xff
        self.stencilFail = KeepStencilOp
        self.stencilZFail = KeepStencilOp
        self.stencilZPass = KeepStencilOp
        self.stencilWrite = False

        self.clippingPlanes = None
        self.clipIntersection = False
        self.clipShadows = False

        self.shadowSide = None

        self.colorWrite = True

        self.precision = None  #override the renderer's default precision for this material

        self.polygonOffset = False
        self.polygonOffsetFactor = 0
        self.polygonOffsetUnits = 0

        self.dithering = False

        self.alphaToCoverage = False
        self.premultipliedAlpha = False

        self.visible = True

        self.toneMapped = True

        self.userData = {}

        self.version = 0

        self._alphaTest = 0

    @property
    def alphaTest(self):
        return self._alphaTest

    @alphaTest.setter
    def alphaTest(self, value):
        if self._alphaTest > 0 != value > 0:
            self.version += 1

        self._alphaTest = value

    def onBuild(self):
        ''' /* shaderobject, renderer */ '''
        pass

    def onBeforeRender(self):
        ''' /* renderer, scene, camera, geometry, object, group */ '''
        pass

    def onBeforeCompile(self):
        '''  /* shaderobject, renderer */ '''
        pass

    def customProgramCacheKey(self):
        return str(self.onBeforeRender)

    
    def setValues(self, values: 'dict|Material'):
        if values is None:
            return

        if isinstance(values, Material):
            values = values.__dict__
        
        for key, val in values.items():
            # if val is None:
            #     warnings.warn(f"THREE.Material: '{key}' parameter is None.")
            #     continue
            
            if key == 'shading':
                warnings.warn(f'THREE.{self.type}: .shading has been removed. Use the boolean .flatShading instead.')
                self.flatShading = val == FlatShading
                continue
            

            if not hasattr(self, key):
                warnings.warn( f"THREE.{self.type}: '{key}' is not a property of this material." )
                continue


            current_value = getattr(self, key)

            if current_value and type(current_value) == Color:
                current_value.set( val )

            elif (current_value and type(current_value) == Vector3 ) and  ( val and type(val) == Vector3 ):
                current_value.copy( val )

            else:
                setattr(self, key, val)


    def clone( self ):
        return Material().copy( self )

    def copy( self, source: 'Material' ):

        self.name = source.name

        self.fog = source.fog

        self.blending = source.blending
        self.side = source.side
        self.vertexColors = source.vertexColors

        self.opacity = source.opacity
        self.format = source.format
        self.transparent = source.transparent

        self.blendSrc = source.blendSrc
        self.blendDst = source.blendDst
        self.blendEquation = source.blendEquation
        self.blendSrcAlpha = source.blendSrcAlpha
        self.blendDstAlpha = source.blendDstAlpha
        self.blendEquationAlpha = source.blendEquationAlpha

        self.depthFunc = source.depthFunc
        self.depthTest = source.depthTest
        self.depthWrite = source.depthWrite

        self.stencilWriteMask = source.stencilWriteMask
        self.stencilFunc = source.stencilFunc
        self.stencilRef = source.stencilRef
        self.stencilFuncMask = source.stencilFuncMask
        self.stencilFail = source.stencilFail
        self.stencilZFail = source.stencilZFail
        self.stencilZPass = source.stencilZPass
        self.stencilWrite = source.stencilWrite

        srcPlanes = source.clippingPlanes
        dstPlanes = None
        if srcPlanes is not None:
            dstPlanes = []
            for p in srcPlanes:
                dstPlanes.append(p.clone())


        self.clippingPlanes = dstPlanes
        self.clipIntersection = source.clipIntersection
        self.clipShadows = source.clipShadows

        self.shadowSide = source.shadowSide

        self.colorWrite = source.colorWrite

        self.precision = source.precision

        self.polygonOffset = source.polygonOffset
        self.polygonOffsetFactor = source.polygonOffsetFactor
        self.polygonOffsetUnits = source.polygonOffsetUnits

        self.dithering = source.dithering

        self.alphaTest = source.alphaTest
        self.alphaToCoverage = source.alphaToCoverage
        self.premultipliedAlpha = source.premultipliedAlpha

        self.visible = source.visible

        self.toneMapped = source.toneMapped

        self.userData = source.userData.copy()

        return self


    def dispose(self):
        self.dispatchEvent( { type: 'dispose' } )

    @property
    def needsUpdate( self ):
        return self._needs_update

    @needsUpdate.setter
    def needsUpdate( self, value):
        self._needs_update = value
        if value:
            self.version += 1
			
