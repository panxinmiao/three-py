from warnings import warn
from ...math import Color
from ...objects import Mesh
from ...geometries import BoxGeometry
from ...constants import BackSide, EquirectangularReflectionMapping, EquirectangularRefractionMapping
from .constants import GPULoadOp, GPUStoreOp
from ...nodes import (NodeMaterial, vec2, uv, context, transformDirection, positionWorld, modelWorldMatrix, 
        invert, texture, cubeTexture, equirectUV, viewportTopLeft)

class WgpuBackground:

    _clearAlpha = 1
    _clearColor = Color()

    def __init__( self, renderer) -> None:
        self.renderer = renderer
        self.boxMesh = None
        self.planeMesh = None
        self.forceClear = False

        self._background = None

    def clear(self):
        self.forceClear = True

    def update( self, renderList, scene ):
        renderer = self.renderer
        background = scene.backgroundNode or scene.background if scene.isScene else None
        forceClear = self.forceClear

        if self._background != background:
            self._background = background
            self.boxMesh = None
        
        if background is None:
            # no background settings, use clear color configuration from the renderer
            WgpuBackground._clearColor.copy( renderer._clearColor )
            WgpuBackground._clearAlpha = renderer._clearAlpha

        elif background.isColor:
            # background is an opaque color
            WgpuBackground._clearColor.copy( background )
            WgpuBackground._clearAlpha = 1
            forceClear = True

        elif background.isNode or background.isTexture:
            WgpuBackground._clearColor.copy(renderer._clearColor)
            WgpuBackground._clearAlpha = renderer._clearAlpha

            boxMesh = self.boxMesh

            if boxMesh is None:
                
                if background.isCubeTexture:
                    # background = CubeTextureNode(background)
                    colorNode = cubeTexture(background, transformDirection( positionWorld, modelWorldMatrix ))
                elif background.isTexture:
                    nodeUV = None

                    if background.mapping == EquirectangularReflectionMapping or background.mapping == EquirectangularRefractionMapping:
                        dirNode = transformDirection(positionWorld, modelWorldMatrix)

                        nodeUV = equirectUV( dirNode )
                        nodeUV = vec2( nodeUV.x, invert(nodeUV.y))
                    else:
                        nodeUV = viewportTopLeft
                    
                    colorNode = texture( background, nodeUV )

                else: # background.isNode
                    colorNode = context(background, {
                        # 'uvNode': transformDirection(positionWorld, modelWorldMatrix)
                        "getUVNode": lambda *args: transformDirection(positionWorld, modelWorldMatrix)
                    })


                nodeMaterial = NodeMaterial()
                nodeMaterial.colorNode = colorNode
                nodeMaterial.side = BackSide
                nodeMaterial.depthTest = False
                nodeMaterial.depthWrite = False
                nodeMaterial.fog = False

                self.boxMesh = boxMesh = Mesh(BoxGeometry(1, 1, 1), nodeMaterial)

                def _onBeforeRender(renderer, scene, camera, geometry, material, group):
                    boxMesh.matrixWorld.copyPosition(camera.matrixWorld)

                boxMesh.onBeforeRender = _onBeforeRender
            
            renderList.unshift(boxMesh, boxMesh.geometry, boxMesh.material, 0, 0, None)
            
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
                colorAttachment.store_op = GPUStoreOp.Store

            if renderer.autoClearDepth:
                depthStencilAttachment.depth_clear_value = renderer._clearDepth
                depthStencilAttachment.depth_load_op = GPULoadOp.Clear
                depthStencilAttachment.depth_store_op = GPUStoreOp.Store

            else:
                depthStencilAttachment.depth_load_op = GPULoadOp.Load
                depthStencilAttachment.depth_store_op = GPUStoreOp.Store


            if renderer.autoClearStencil:
                depthStencilAttachment.stencil_clear_value = renderer._clearStencil
                depthStencilAttachment.stencil_load_op = GPULoadOp.Clear
                depthStencilAttachment.stencil_store_op = GPUStoreOp.Store

            else:
                depthStencilAttachment.stencil_load_op = GPULoadOp.Load
                depthStencilAttachment.stencil_store_op = GPUStoreOp.Store

        else:

            colorAttachment.load_op = GPULoadOp.Load
            depthStencilAttachment.depth_load_op = GPULoadOp.Load
            depthStencilAttachment.stencil_load_op = GPULoadOp.Load


        self.forceClear = False


# class BackgroundNodeMaterial(NodeMaterial):

#     def __init__(self, parameters=None) -> None:
#         super().__init__()
#         self.lights = False

#     def generatePosition(self, builder):
#         # < VERTEX STAGE >

#         vertex = vec4(positionLocal.xy, 1.0, 1.0)

#         builder.context.vertex = vertex

#         builder.addFlow( 'vertex', vertex )