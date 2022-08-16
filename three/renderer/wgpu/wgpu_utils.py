from .constants import GPUPrimitiveTopology, GPUTextureFormat

class WgpuUtils:

    def __init__(self, renderer) -> None:
        self.renderer = renderer
    
    def getCurrentEncoding(self):
        renderer = self.renderer
        renderTarget = renderer.getRenderTarget()

        if renderTarget is not None:
            return renderTarget.texture.encoding
        else:
            return renderer.outputEncoding

    def getCurrentColorFormat(self):
        format = None

        renderer = self.renderer
        renderTarget = renderer.getRenderTarget()

        if renderTarget is not None:
            renderTargetProperties = renderer._properties.get( renderTarget )
            format = renderTargetProperties.colorTextureFormat
        else:
            format = GPUTextureFormat.BGRA8Unorm  # default context format

        return format
    
    def getCurrentDepthStencilFormat(self):
        format = None

        renderer = self.renderer
        renderTarget = renderer.getRenderTarget()

        if renderTarget is not None:
            renderTargetProperties = renderer._properties.get( renderTarget )
            format = renderTargetProperties.depthTextureFormat
        else:
            format = GPUTextureFormat.Depth24PlusStencil8

        return format

    def getPrimitiveTopology( self, object ):
        if object.isMesh or object.isSprite:
            return GPUPrimitiveTopology.TriangleList
        elif object.isPoints:
            return GPUPrimitiveTopology.PointList
        elif object.isLineSegments:
            return GPUPrimitiveTopology.LineList
        elif object.isLine:
            return GPUPrimitiveTopology.LineStrip

    def getSampleCount(self):
        return self.renderer._parameters.sampleCount