from ..core import EventDispatcher
from ..math import Vector4
from ..textures import Texture
from ..structure import Dict
from ..constants import LinearFilter

class RenderTarget(EventDispatcher):

    def __init__(self, width, height, options = {}) -> None:
        super().__init__()

        options = Dict(options)

        self.width = width
        self.height = height
        self.depth = 1

        self.scissor = Vector4( 0, 0, width, height )
        self.scissorTest = False

        self.viewport = Vector4( 0, 0, width, height )

        image = { 'width': width, 'height': height, 'depth': 1 }

        self.texture = Texture( image, options.mapping, options.wrapS, options.wrapT, options.magFilter, options.minFilter, options.format, options.type, options.anisotropy, options.encoding )
        self.texture.isRenderTargetTexture = True

        self.texture.generateMipmaps = options.generateMipmaps if options.generateMipmaps else False

        self.texture.internalFormat = options.internalFormat if options.internalFormat else None

        self.texture.minFilter = options.minFilter if options.minFilter else LinearFilter

        self.depthBuffer = options.depthBuffer if options.depthBuffer else True
        self.stencilBuffer = options.stencilBuffer if options.stencilBuffer else False
        self.depthTexture = options.depthTexture if options.depthTexture else None

    
    def setTexture( self, texture ):

        texture.image = {
            'width': self.width,
            'height': self.height,
            'depth': self.depth
        }

        self.texture = texture

    def setSize(self, width, height, depth = 1 ):

        if self.width != width or self.height != height or self.depth != depth:

            self.width = width
            self.height = height
            self.depth = depth

            self.texture.image.width = width
            self.texture.image.height = height
            self.texture.image.depth = depth

            self.dispose()

        self.viewport.set( 0, 0, width, height )
        self.scissor.set( 0, 0, width, height )


    def clone(self):
        return RenderTarget().copy()

    def copy( self, source ):
        self.width = source.width
        self.height = source.height
        self.depth = source.depth

        self.viewport.copy( source.viewport )

        self.texture = source.texture.clone()

        # ensure image object is not shared, see #20328

        self.texture.image = {**source.texture.image}

        self.depthBuffer = source.depthBuffer
        self.stencilBuffer = source.stencilBuffer
        self.depthTexture = source.depthTexture

        return self



    def dispose(self):
        self.dispatchEvent( { type: 'dispose' } )
