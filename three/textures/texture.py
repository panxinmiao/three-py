#import constants as Const
import uuid, math

from ..core import EventDispatcher
from ..constants import MirroredRepeatWrapping, ClampToEdgeWrapping, RepeatWrapping, LinearEncoding
from ..constants import UnsignedByteType, RGBAFormat, LinearMipmapLinearFilter, LinearFilter, UVMapping
from ..math import Vector2, Matrix3
from .source import Source

_texture_id = 0

class Texture(EventDispatcher):

    DEFAULT_IMAGE = None
    DEFAULT_MAPPING = UVMapping

    def __init__(self, image=DEFAULT_IMAGE, mapping = DEFAULT_MAPPING, wrapS = ClampToEdgeWrapping,
                    wrapT = ClampToEdgeWrapping, magFilter = LinearFilter, minFilter = LinearMipmapLinearFilter, 
                    format = RGBAFormat, type = UnsignedByteType, anisotropy = 1, encoding = LinearEncoding) -> None:

        global _texture_id
        _texture_id += 1
        self.id = _texture_id
        self.uuid = uuid.uuid1()

        self.name = ''
        self.source = Source(image)
        self.mipmaps = []

        self.mapping = mapping

        self.wrapS = wrapS
        self.wrapT = wrapT

        self.magFilter = magFilter
        self.minFilter = minFilter

        self.anisotropy = anisotropy

        self.format = format
        self.internalFormat = None
        self.type = type

        self.offset = Vector2( 0, 0 )
        self.repeat = Vector2( 1, 1 )
        self.center = Vector2( 0, 0 )
        self.rotation = 0

        self.matrixAutoUpdate = True
        self.matrix = Matrix3()

        self.generateMipmaps = True
        self.premultiplyAlpha = False
        self.flipY = True
        self.unpackAlignment = 4	# valid values: 1, 2, 4, 8 (see http://www.khronos.org/opengles/sdk/docs/man/xhtml/glPixelStorei.xml)

        self.encoding = encoding

        self.userData = {}

        self.version = 0
        self.onUpdate = None

        self.isRenderTargetTexture = False
        self.needsPMREMUpdate = False

    @property
    def image(self):
        return self.source.data

    @image.setter
    def image(self, value):
        self.source.data = value

    def updateMatrix(self):
        self.matrix.setUvTransform( self.offset.x, self.offset.y, self.repeat.x, self.repeat.y, self.rotation, self.center.x, self.center.y )


    def clone(self):
        return self.__class__().copy( self )


    def copy(self, source: 'Texture'):
        
        self.name = source.name

        self.image = source.image
        self.mipmaps = source.mipmaps.copy()

        self.mapping = source.mapping

        self.wrapS = source.wrapS
        self.wrapT = source.wrapT

        self.magFilter = source.magFilter
        self.minFilter = source.minFilter

        self.anisotropy = source.anisotropy

        self.format = source.format
        self.internalFormat = source.internalFormat
        self.type = source.type

        self.offset.copy( source.offset )
        self.repeat.copy( source.repeat )
        self.center.copy( source.center )
        self.rotation = source.rotation

        self.matrixAutoUpdate = source.matrixAutoUpdate
        self.matrix.copy( source.matrix )

        self.generateMipmaps = source.generateMipmaps
        self.premultiplyAlpha = source.premultiplyAlpha
        self.flipY = source.flipY
        self.unpackAlignment = source.unpackAlignment
        self.encoding = source.encoding

        self.userData = source.userData.copy()

        return self

    def transformUv(self, uv: 'Vector2' ):

        if self.mapping != UVMapping:
            return uv

        uv.applyMatrix3( self.matrix )

        if uv.x < 0 or uv.x > 1:
            if self.wrapS == RepeatWrapping:
                uv.x = uv.x - math.floor( uv.x )
            elif self.wrapS == ClampToEdgeWrapping:
                uv.x = 0 if uv.x < 0 else 1
            elif self.wrapS == MirroredRepeatWrapping:

                if abs( math.floor( uv.x ) % 2 ) == 1:
                    uv.x = math.ceil( uv.x ) - uv.x
                else:
                    uv.x = uv.x - math.floor( uv.x )


        if uv.y < 0 or uv.y > 1:

            if self.wrapT == RepeatWrapping:
                uv.y = uv.y - math.floor( uv.y )
            elif self.wrapT == ClampToEdgeWrapping:
                uv.y = 0 if uv.y < 0 else 1
            elif self.wrapT == MirroredRepeatWrapping:
                if ( abs( math.floor( uv.y ) % 2 ) == 1 ):
                    uv.y = math.ceil( uv.y ) - uv.y
                else:
                    uv.y = uv.y - math.floor( uv.y )


        if self.flipY:
            uv.y = 1 - uv.y

        return uv

    @property
    def needsUpdate( self ):
        return None

    @needsUpdate.setter
    def needsUpdate( self, value):
        if value == True:
            self.version += 1
            self.source.needsUpdate = True





