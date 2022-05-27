import wgpu
import math
from warnings import warn

from ...structure import Dict
from ...materials import Texture, CubeTexture
from ...constants import (NearestFilter, NearestMipmapNearestFilter, NearestMipmapLinearFilter, LinearFilter, RepeatWrapping, MirroredRepeatWrapping,
            RGBAFormat, RedFormat, RGFormat, RGBA_S3TC_DXT1_Format, RGBA_S3TC_DXT3_Format, RGBA_S3TC_DXT5_Format, UnsignedByteType, FloatType, HalfFloatType, sRGBEncoding)
from .constants import GPUTextureFormat, GPUAddressMode, GPUFilterMode, GPUTextureDimension, GPUTextureUsage
from .wgpu_texture_utils import WgpuTextureUtils

class WgpuTextures:

    def __init__(self, device: 'wgpu.GPUDevice', properties, info) -> None:
        self.device = device
        self.properties = properties
        self.info = info

        self.defaultTexture = None
        self.defaultCubeTexture = None
        self.defaultSampler = None

        self.samplerCache = {}
        self.utils = None

    
    def getDefaultSampler(self):

        if self.defaultSampler is None:
            self.defaultSampler = self.device.create_sampler()
        
        return self.defaultSampler

    def getDefaultTexture(self):
        
        if self.defaultTexture is None:

            texture = Texture()
            texture.minFilter = NearestFilter
            texture.magFilter = NearestFilter
            
            self._uploadTexture( texture )

            self.defaultTexture = self.getTextureGPU( texture )
        
        return self.defaultTexture

    def getDefaultCubeTexture(self):
        
        if self.defaultCubeTexture is None:
            
            texture = CubeTexture()
            texture.minFilter = NearestFilter
            texture.magFilter = NearestFilter

            self._uploadTexture( texture )

            self.defaultCubeTexture = self.getTextureGPU( texture )

        return self.defaultCubeTexture

    def getTextureGPU( self, texture ):
        textureProperties = self.properties.get( texture )
        
        return textureProperties.textureGPU

    def getSampler(self, texture ):
        textureProperties = self.properties.get( texture )
        
        return textureProperties.samplerGPU

    def updateTexture(self, texture ):

        needsUpdate = False

        textureProperties = self.properties.get( texture )

        if texture.version > 0 and textureProperties.version != texture.version:
            
            image = texture.image
            if not image:
                warn( 'THREE.WebGPURenderer: Texture marked for update but image is None.' )

            else:
                # texture init
                if textureProperties.initialized is None:
                    textureProperties.initialized = True
                    disposeCallback = self.onTextureDispose
                    
                    textureProperties.disposeCallback = disposeCallback

                    texture.addEventListener( 'dispose', disposeCallback )
                    
                    self.info.memory.textures +=1

                needsUpdate = self._uploadTexture( texture )


        # if the texture is used for RTT, it's necessary to init it once so the binding
        # group's resource definition points to the respective GPUTexture

        if textureProperties.initializedRTT == False:
            textureProperties.initializedRTT = True
            needsUpdate = True
            
        return needsUpdate

    
    def updateSampler( self, texture ):
        array = []
        
        array.append( texture.wrapS )
        array.append( texture.wrapT )
        array.append( texture.wrapR )
        array.append( texture.magFilter )
        array.append( texture.minFilter )
        array.append( texture.anisotropy )

        key = ','.join( map( str, array ) )
        
        samplerGPU = self.samplerCache.get( key )
        if samplerGPU is None:
            samplerGPU = self.device.create_sampler(
                address_mode_u = self._convertAddressMode( texture.wrapS ),
                address_mode_v = self._convertAddressMode( texture.wrapT ),
                address_mode_w = self._convertAddressMode( texture.wrapR ),
                mag_filter = self._convertFilterMode( texture.magFilter ),
                min_filter = self._convertFilterMode( texture.minFilter ),
                mipmap_filter = self._convertFilterMode( texture.minFilter ),
                max_anisotropy = texture.anisotropy
            )

            self.samplerCache[key] = samplerGPU
        
        textureProperties = self.properties.get( texture )
        textureProperties.samplerGPU = samplerGPU

    
    def initRenderTarget( self, renderTarget ):

        properties = self.properties
        renderTargetProperties = properties.get( renderTarget )

        if renderTargetProperties.initialized is None:
            device = self.device

            width = renderTarget.width
            height = renderTarget.height
            colorTextureFormat = self._getFormat( renderTarget.texture )

            colorTextureGPU = device.create_texture(
                size={
                    'width': width,
                    'height': height,
                    'depth_or_array_layers': 1
                },
                format=colorTextureFormat,
                usage=GPUTextureUsage.RENDER_ATTACHMENT | GPUTextureUsage.TEXTURE_BINDING
            )

            self.info.memory.textures += 1

            renderTargetProperties.colorTextureGPU = colorTextureGPU
            renderTargetProperties.colorTextureFormat = colorTextureFormat

            # When the ".texture" or ".depthTexture" property of a render target is used as a map,
            # the renderer has to find the respective GPUTexture objects to setup the bind groups.
            # Since it's not possible to see just from a texture object whether it belongs to a render
            # target or not, we need the initializedRTT flag.

            textureProperties = properties.get( renderTarget.texture )
            textureProperties.textureGPU = colorTextureGPU
            textureProperties.initializedRTT = False

            if renderTarget.depthBuffer == True:
                depthTextureFormat = GPUTextureFormat.Depth24PlusStencil8  # @TODO: Make configurable

                depthTextureGPU = device.create_texture(
                    size =  {
                        'width': width,
                        'height': height,
                        'depth_or_array_layers': 1
                    },
                    format = depthTextureFormat,
                    usage= GPUTextureUsage.RENDER_ATTACHMENT
                )

                self.info.memory.textures += 1

                renderTargetProperties.depthTextureGPU = depthTextureGPU
                renderTargetProperties.depthTextureFormat = depthTextureFormat

                if renderTarget.depthTexture is not None:
                    depthTextureProperties = properties.get( renderTarget.depthTexture )
                    depthTextureProperties.textureGPU = depthTextureGPU
                    depthTextureProperties.initializedRTT = False

            disposeCallback = self.onRenderTargetDispose
            renderTargetProperties.disposeCallback = disposeCallback

            renderTarget.addEventListener( 'dispose', disposeCallback )

            renderTargetProperties.initialized = True


    def dispose(self):
        self.samplerCache.clear()


    def _convertAddressMode( self, value ):
        addressMode = GPUAddressMode.ClampToEdge

        if value == RepeatWrapping:
            addressMode = GPUAddressMode.Repeat
        elif value == MirroredRepeatWrapping:
            addressMode = GPUAddressMode.MirrorRepeat
        
        return addressMode

    def _convertFilterMode( self, value ):
        filterMode = GPUFilterMode.Linear
        
        if value == NearestFilter or value == NearestMipmapNearestFilter or value == NearestMipmapLinearFilter:
            filterMode = GPUFilterMode.Nearest
        
        return filterMode

    def _uploadTexture( self, texture ):

        needsUpdate = False

        device = self.device
        image = texture.image

        textureProperties = self.properties.get( texture )

        width, height, depth = self._getSize( texture )
        needsMipmaps = self._needsMipmaps( texture )
        dimension = self._getDimension( texture )
        mipLevelCount = self._getMipLevelCount( texture, width, height, needsMipmaps )
        format = self._getFormat( texture )

        usage = GPUTextureUsage.TEXTURE_BINDING | GPUTextureUsage.COPY_DST

        if needsMipmaps == True:
            # current mipmap generation requires RENDER_ATTACHMENT
            usage |= GPUTextureUsage.RENDER_ATTACHMENT


        textureGPUDescriptor = Dict({
            'size': {
                'width': width,
                'height': height,
                'depth_or_array_layers': depth,
            },
            'mip_level_count': mipLevelCount,
            'sample_count': 1,
            'dimension': dimension,
            'format': format,
            'usage': usage
        })

        # texture creation

        textureGPU = textureProperties.textureGPU

        if textureGPU is None:
            textureGPU = device.create_texture( **textureGPUDescriptor )
            textureProperties.textureGPU = textureGPU

            needsUpdate = True

        # transfer texture data

        # always dataTexture at present
        if texture.isDataTexture or texture.isDataTexture2DArray or texture.isDataTexture3D:
            self._copyBufferToTexture( image, format, textureGPU )

            if needsMipmaps == True:
                self._generateMipmaps( textureGPU, textureGPUDescriptor )

        elif texture.isCompressedTexture:
            self._copyCompressedBufferToTexture( texture.mipmaps, format, textureGPU )

        elif texture.isCubeTexture:
            if len(image) == 6:
                self._copyCubeMapToTexture( image, format, texture, textureGPU, textureGPUDescriptor, needsMipmaps )

        else:
            if image is not None:
                self._copyBufferToTexture(image, format, textureGPU)

                if needsMipmaps == True:
                    self._generateMipmaps( textureGPU, textureGPUDescriptor )


        textureProperties.version = texture.version

        return needsUpdate

    # def _copyBufferToTexture(self, image, format, textureGPU, origin=(0, 0, 0)):

    #     # @TODO: Consider to use GPUCommandEncoder.copyBufferToTexture()
    #     # @TODO: Consider to support valid buffer layouts with other formats like RGB

    #     data = image.data

    #     bytesPerTexel = self._getBytesPerTexel(format)
    #     bytesPerRow = math.ceil(image.width * bytesPerTexel / 256) * 256

    #     queue: wgpu.GPUQueue = self.device.queue

    #     commandEncoder: wgpu.GPUCommandEncoder = self.device.create_command_encoder()
    #     commandEncoder.copy_buffer_to_texture(
    #         {
    #             'buffer': data,
    #             'offset': 0,
    #             'bytes_per_row': bytesPerRow
    #         },
    #         {
    #             'texture': textureGPU,
    #             'mip_level': 0,
    #             'origin': origin
    #         },
    #         (image.width, image.height, image.depth if image.depth is not None else 1)
    #     )
    #     queue.submit([commandEncoder.finish()])


    def _copyBufferToTexture( self, image, format, textureGPU, origin = (0, 0, 0) ):

        # @TODO: Consider to use GPUCommandEncoder.copyBufferToTexture()
        # @TODO: Consider to support valid buffer layouts with other formats like RGB
        data = image.data
        bytesPerTexel = self._getBytesPerTexel( format )
        bytesPerRow = math.ceil( image.width * bytesPerTexel / 256 ) * 256

        queue: wgpu.GPUQueue = self.device.queue

        queue.write_texture(
            {
                'texture': textureGPU,
                'mip_level': 0,
                'origin': origin
            },
            data,
            {
                'offset': 0,
                'bytes_per_row': bytesPerRow
            },
            (image.width, image.height, image.depth if image.depth is not None else 1)
        )

    def _copyCubeMapToTexture( self, images, format, texture, textureGPU, textureGPUDescriptor, needsMipmaps ):
        
        for i in range(6):
            image = images[ i ]
            self._copyBufferToTexture( image, format, textureGPU, (0, 0, i) )

            if needsMipmaps:
                self._generateMipmaps( textureGPU, textureGPUDescriptor, i )


    def _copyCompressedBufferToTexture(self, mipmaps, format, textureGPU ):

        # @TODO: Consider to use GPUCommandEncoder.copyBufferToTexture()

        blockData = self._getBlockData( format )
        
        for i in range(len(mipmaps)):
            mipmap = mipmaps[ i ] 
            width = mipmap.width
            height = mipmap.height

            bytesPerRow = math.ceil( width / blockData.width ) * blockData.byteLength

            queue: wgpu.GPUQueue = self.device.queue

            queue.write_texture(
                {
                    'texture': textureGPU,
                    'mipLevel': i
                },
                mipmap.data,
                {
                    'offset': 0,
                    'bytes_per_row': bytesPerRow
                },
                (math.ceil( width / blockData.width ) * blockData.width, math.ceil( height / blockData.width ) * blockData.width, 1)
            )

    def _generateMipmaps(self, textureGPU, textureGPUDescriptor, baseArrayLayer=0):
        
        if self.utils is None:
            self.utils = WgpuTextureUtils( self.device );  # only create this helper if necessary

        self.utils.generateMipmaps( textureGPU, textureGPUDescriptor, baseArrayLayer)

    
    def _getBlockData( self, format ):

		# this method is only relevant for compressed texture formats
        if format == GPUTextureFormat.BC1RGBAUnorm or format == GPUTextureFormat.BC1RGBAUnormSRGB:
            return { 'byteLength': 8, 'width': 4, 'height': 4 }; # DXT1
        if format == GPUTextureFormat.BC2RGBAUnorm or format == GPUTextureFormat.BC2RGBAUnormSRGB:
            return { 'byteLength': 16, 'width': 4, 'height': 4 }; # DXT3
        if format == GPUTextureFormat.BC3RGBAUnorm or format == GPUTextureFormat.BC3RGBAUnormSRGB:
            return { 'byteLength': 16, 'width': 4, 'height': 4 }; # DXT5
        if format == GPUTextureFormat.BC4RUnorm or format == GPUTextureFormat.BC4RSNorm:
            return { 'byteLength': 8, 'width': 4, 'height': 4 }; # RGTC1
        if format == GPUTextureFormat.BC5RGUnorm or format == GPUTextureFormat.BC5RGSnorm:
            return { 'byteLength': 16, 'width': 4, 'height': 4 }; # RGTC2
        if format == GPUTextureFormat.BC6HRGBUFloat or format == GPUTextureFormat.BC6HRGBFloat:
            return { 'byteLength': 16, 'width': 4, 'height': 4 }; # BPTC (float)
        if format == GPUTextureFormat.BC7RGBAUnorm or format == GPUTextureFormat.BC7RGBAUnormSRGB:
            return { 'byteLength': 16, 'width': 4, 'height': 4 }; # BPTC (unorm)

    def _getBytesPerTexel( self, format ):
        if format == GPUTextureFormat.R8Unorm:
            return 1
        if format == GPUTextureFormat.R16Float:
            return 2
        if format == GPUTextureFormat.RG8Unorm:
            return 2
        if format == GPUTextureFormat.RG16Float:
            return 4
        if format == GPUTextureFormat.R32Float:
            return 4
        if format == GPUTextureFormat.RGBA8Unorm or format == GPUTextureFormat.RGBA8UnormSRGB:
            return 4
        if format == GPUTextureFormat.RG32Float:
            return 8
        if format == GPUTextureFormat.RGBA16Float:
            return 8
        if format == GPUTextureFormat.RGBA32Float:
            return 16

    def _getDimension( self, texture ):

        dimension = GPUTextureDimension.ThreeD if texture.isDataTexture3D else GPUTextureDimension.TwoD

        return dimension

    def _getFormat( self, texture ):
        format = texture.format
        type = texture.type
        encoding = texture.encoding

        if format == RGBA_S3TC_DXT1_Format:
            return GPUTextureFormat.BC1RGBAUnormSRGB if encoding == sRGBEncoding else GPUTextureFormat.BC1RGBAUnorm
        
        if format == RGBA_S3TC_DXT3_Format:
            return GPUTextureFormat.BC2RGBAUnormSRGB if encoding == sRGBEncoding else GPUTextureFormat.BC2RGBAUnorm
        
        if format == RGBA_S3TC_DXT5_Format:
            return GPUTextureFormat.BC3RGBAUnormSRGB if encoding == sRGBEncoding else GPUTextureFormat.BC3RGBAUnorm

        if format == RGBAFormat:

            if type == UnsignedByteType:
                return GPUTextureFormat.RGBA8UnormSRGB if encoding == sRGBEncoding else GPUTextureFormat.RGBA8Unorm
            if type == HalfFloatType:
                return GPUTextureFormat.RGBA16Float
            if type == FloatType:
                return GPUTextureFormat.RGBA32Float
            
            warn( f'WebGPURenderer: Unsupported texture type with RGBAFormat.{type}' )
            return
        
        if format == RedFormat:
            if type == UnsignedByteType:
                return GPUTextureFormat.R8Unorm
            if type == HalfFloatType:
                return GPUTextureFormat.R16Float
            if type == FloatType:
                return GPUTextureFormat.R32Float
            
            warn( f'WebGPURenderer: Unsupported texture type with RedFormat.{type}')
            return

        if format == RGFormat:
            if type == UnsignedByteType:
                return GPUTextureFormat.RG8Unorm
            if type == HalfFloatType:
                return GPUTextureFormat.RG16Float
            if type == FloatType:
                return GPUTextureFormat.RG32Float
            
            warn( f'WebGPURenderer: Unsupported texture type with RGFormat.{type}')
            return

        warn( f'WebGPURenderer: Unsupported texture format.{format}')


    def _getImageBitmap( self, image, texture ):
        # TODO consider image data structure
        return image

    def _getMipLevelCount( self, texture, width, height, needsMipmaps ):

        if texture.isCompressedTexture:
            return texture.mipmaps.length

        elif needsMipmaps == True:

            return math.floor( math.log2( max( width, height ) ) ) + 1

        else:
            
            return 1  # a texture without mipmaps has a base mip (mipLevel 0)

    def _getSize( self, texture ):
        
        image = texture.image

        if texture.isCubeTexture:
            faceImage = image[0].image or image[0] if len(image) > 0 else None

            width = faceImage.width if faceImage else 1
            height = faceImage.height if faceImage else 1

            depth = 6 # one image for each side of the cube map

        elif image is not None:
            width = image.width
            height = image.height
            depth = image.depth if image.depth != None else 1

        else:
            width = height = depth = 1

        return (width, height, depth)


    def _needsMipmaps( self, texture ):

        return (texture.isCompressedTexture != True) and (texture.generateMipmaps == True) and (texture.minFilter != NearestFilter) and ( texture.minFilter != LinearFilter )


    def onRenderTargetDispose( self, event ):
        renderTarget = event.target
        properties = self.properties

        renderTargetProperties = properties.get( renderTarget )

        renderTarget.removeEventListener( 'dispose', renderTargetProperties.disposeCallback )

        renderTargetProperties.colorTextureGPU.destroy()
        properties.remove( renderTarget.texture )

        self.info.memory.textures -= 1

        if renderTarget.depthBuffer == True:

            renderTargetProperties.depthTextureGPU.destroy()

            self.info.memory.textures -= 1

            if renderTarget.depthTexture is not None:

                properties.remove( renderTarget.depthTexture )


        properties.remove( renderTarget )



    def onTextureDispose( self, event ):

        texture = event.target

        textureProperties = self.properties.get( texture )
        textureProperties.textureGPU.destroy()

        texture.removeEventListener( 'dispose', textureProperties.disposeCallback )
        
        self.properties.remove( texture )

        self.info.memory.textures -= 1

