from warnings import warn
from ...math import Color
from .constants import GPULoadOp, GPUStoreOp

class WgpuBackground:

    _clearAlpha = 1
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
                colorAttachment.clear_value = (WgpuBackground._clearColor.r, WgpuBackground._clearColor.g, WgpuBackground._clearColor.b, WgpuBackground._clearAlpha)
                colorAttachment.load_op = GPULoadOp.Clear
                colorAttachment.store_op = GPUStoreOp.Store

            else:
                colorAttachment.load_op = GPULoadOp.Load

            if renderer.autoClearDepth:
                depthStencilAttachment.depth_clear_value = renderer._clearDepth
                depthStencilAttachment.depth_load_op = GPULoadOp.Clear

            else:
                depthStencilAttachment.depth_load_op = GPULoadOp.Load


            if renderer.autoClearStencil:
                depthStencilAttachment.stencil_clear_value = renderer._clearStencil
                depthStencilAttachment.stencil_load_op = GPULoadOp.Clear

            else:
                depthStencilAttachment.stencil_load_op = GPULoadOp.Load


        else:

            colorAttachment.load_op = GPULoadOp.Load
            depthStencilAttachment.depth_load_op = GPULoadOp.Load
            depthStencilAttachment.stencil_load_op = GPULoadOp.Load


        self.forceClear = False
