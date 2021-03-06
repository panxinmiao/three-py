from warnings import warn
from ...math import Color
from ...objects import Mesh
from ...geometries import BoxGeometry, PlaneGeometry
from ...nodes.shadernode.shader_node_base_elements import context, transformDirection, positionWorld, modelWorldMatrix
from ...nodes.materials.mesh_basic_node_material import MeshBasicNodeMaterial
from ...nodes.accessors.cube_texture_node import CubeTextureNode
from ...nodes.accessors.texture_node import TextureNode
from ...constants import BackSide
from .constants import GPULoadOp, GPUStoreOp

from ...nodes import NodeMaterial, vec2, vec4, positionLocal, UVNode, nodeObject

class WgpuBackground:

    _clearAlpha = 1
    _clearColor = Color()

    def __init__( self, renderer) -> None:
        self.renderer = renderer
        self.boxMesh = None
        self.planeMesh = None
        self.forceClear = False

    def clear(self):
        self.forceClear = True

    def update( self, renderList, scene ):
        renderer = self.renderer
        background = scene.backgroundNode or scene.background if scene.isScene else None
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

        elif background.isCubeTextureNode or background.isCubeTexture:
            WgpuBackground._clearColor.copy(renderer._clearColor)
            WgpuBackground._clearAlpha = renderer._clearAlpha

            boxMesh = self.boxMesh

            if background.isCubeTexture:
                background = CubeTextureNode(background)

            if boxMesh is None:
                colorNode = context(background, {
                    'uvNode': transformDirection(positionWorld, modelWorldMatrix)
                })

                nodeMaterial = MeshBasicNodeMaterial()
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

        elif background.isTextureNode or background.isTexture:
            WgpuBackground._clearColor.copy(renderer._clearColor)
            WgpuBackground._clearAlpha = renderer._clearAlpha

            planeMesh = self.planeMesh

            if background.isTexture:
                background = TextureNode(background)

            if planeMesh is None:
                uv = nodeObject(UVNode())
                background.uvNode =  vec2(uv.x, -uv.y + 1)
                nodeMaterial = BackgroundNodeMaterial()
                nodeMaterial.colorNode = background
                nodeMaterial.depthTest = False
                nodeMaterial.depthWrite = False
                nodeMaterial.fog = False

                self.planeMesh = planeMesh = Mesh(PlaneGeometry(2, 2), nodeMaterial)

            renderList.unshift(planeMesh, planeMesh.geometry, planeMesh.material, 0, 0, None)
            
        else:
            warn( f'THREE.WebGPURenderer: Unsupported background configuration.{background}' )


        # configure render pass descriptor

        renderPassDescriptor = renderer._renderPassDescriptor
        colorAttachment = renderPassDescriptor.color_attachments[ 0 ]
        depthStencilAttachment = renderPassDescriptor.depth_stencil_attachment

        if renderer.autoClear or forceClear:
            if renderer.autoClearColor or forceClear:
                WgpuBackground._clearColor.multiplyScalar( WgpuBackground._clearAlpha )
                colorAttachment.clear_value = (WgpuBackground._clearColor.r, WgpuBackground._clearColor.g, WgpuBackground._clearColor.b, WgpuBackground._clearAlpha)
                colorAttachment.load_op = GPULoadOp.Clear
                colorAttachment.store_op = GPUStoreOp.Store

            else:
                colorAttachment.load_op = GPULoadOp.Load

            if renderer.autoClearDepth or forceClear:
                depthStencilAttachment.depth_clear_value = renderer._clearDepth
                depthStencilAttachment.depth_load_op = GPULoadOp.Clear

            else:
                depthStencilAttachment.depth_load_op = GPULoadOp.Load


            if renderer.autoClearStencil or forceClear:
                depthStencilAttachment.stencil_clear_value = renderer._clearStencil
                depthStencilAttachment.stencil_load_op = GPULoadOp.Clear

            else:
                depthStencilAttachment.stencil_load_op = GPULoadOp.Load


        else:

            colorAttachment.load_op = GPULoadOp.Load
            depthStencilAttachment.depth_load_op = GPULoadOp.Load
            depthStencilAttachment.stencil_load_op = GPULoadOp.Load


        self.forceClear = False


class BackgroundNodeMaterial(NodeMaterial):

    def __init__(self, parameters=None) -> None:
        super().__init__()
        self.lights = False

    def generatePosition(self, builder):
        # < VERTEX STAGE >

        vertex = vec4(positionLocal.xy, 1.0, 1.0)

        builder.context.vertex = vertex

        builder.addFlow( 'vertex', vertex )