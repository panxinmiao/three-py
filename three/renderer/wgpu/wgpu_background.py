from warnings import warn
from ...math import Color
from .constants import GPULoadOp, GPUStoreOp

class WgpuBackground:

    _clearAlpha = None
    _clearColor = Color()

    def __init__( self, renderer) -> None:
        self.renderer = renderer
        self.forceClear = False

    def clear(self):
        self.forceClear = True

    def update( self, scene ):
        renderer = self.renderer
        background = scene.background if scene.isScene else None
        forceClear = self.forceClear
        
        if background is None:
            # no background settings, use clear color configuration from the renderer
            WgpuBackground._clearColor.copy( renderer._clearColor )
            WgpuBackground._clearAlpha = renderer._clearAlpha

        elif background.isColor:
            # background is an opaque color
            WgpuBackground._clearColor.copy( background )
            WgpuBackground._clearAlpha = 1
            forceClear = True

        else:
            warn( f'THREE.WebGPURenderer: Unsupported background configuration.{background}' )


        # configure render pass descriptor

        renderPassDescriptor = renderer._renderPassDescriptor
        colorAttachment = renderPassDescriptor.color_attachments[ 0 ]
        depthStencilAttachment = renderPassDescriptor.depth_stencil_attachment

        if renderer.autoClear or forceClear:
            if renderer.autoClearColor:
                WgpuBackground._clearColor.multiplyScalar( WgpuBackground._clearAlpha )
                # colorAttachment.clear_value = { 'r': WgpuBackground._clearColor.r, 'g': WgpuBackground._clearColor.g, 'b': WgpuBackground._clearColor.b, 'a': WgpuBackground._clearAlpha }
                # colorAttachment.load_value = GPULoadOp.Clear
                colorAttachment.load_value = { 'r': WgpuBackground._clearColor.r, 'g': WgpuBackground._clearColor.g, 'b': WgpuBackground._clearColor.b, 'a': WgpuBackground._clearAlpha }
                colorAttachment.store_op = GPUStoreOp.Store

            else:
                colorAttachment.load_value = GPULoadOp.Load

            if renderer.autoClearDepth:
                #depthStencilAttachment.depthClearValue = renderer._clearDepth
                #depthStencilAttachment.depthLoadOp = GPULoadOp.Clear
                depthStencilAttachment.depth_load_value = renderer._clearDepth

            else:
                depthStencilAttachment.depth_load_value = GPULoadOp.Load


            if renderer.autoClearStencil:
                # depthStencilAttachment.stencilClearValue = renderer._clearStencil
                # depthStencilAttachment.stencilLoadOp = GPULoadOp.Clear
                depthStencilAttachment.stencil_load_value = renderer._clearStencil

            else:
                depthStencilAttachment.stencil_load_value = GPULoadOp.Load


        else:

            colorAttachment.load_value = GPULoadOp.Load
            depthStencilAttachment.depth_load_value = GPULoadOp.Load
            depthStencilAttachment.stencil_load_value = GPULoadOp.Load


        self.forceClear = False
