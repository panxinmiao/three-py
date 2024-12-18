import wgpu, math, three
from warnings import warn
from ...structure import Dict, Uint16Array, NoneAttribute
from ...math import Color, Frustum, Matrix4, Vector3

from .wgpu_objects import WgpuObjects
from .wgpu_attributes import WgpuAttributes
from .wgpu_geometries import WgpuGeometries
from .wgpu_info import WgpuInfo
from .wgpu_properties import WgpuProperties
from .wgpu_render_pipelines import WgpuRenderPipelines
from .wgpu_compute_pipelines import WgpuComputePipelines
from .wgpu_bindings import WgpuBindings                                      
from .wgpu_render_lists import WgpuRenderLists
from .wgpu_render_state import WebGPURenderStates
from .wgpu_textures import WgpuTextures
from .wgpu_background import WgpuBackground
from .nodes.wgpu_nodes import WgpuNodes
from .wgpu_utils import WgpuUtils

from ...constants import LinearEncoding, NoToneMapping
from .constants import GPUStoreOp, GPUTextureFormat, GPUIndexFormat, GPUTextureUsage

_frustum = Frustum()
_projScreenMatrix = Matrix4()
_vector3 = Vector3()

class WgpuRenderer(NoneAttribute):

    isWgpuRenderer = True

    def __init__(self, canvas:'wgpu.WgpuCanvasInterface', parameters:dict={}, **kwargs) -> None:

        parameters = parameters.copy()
        parameters.update(kwargs)
        parameters = Dict(parameters)
        # public

        # if canvas is None:
        #     from wgpu.gui.auto import WgpuCanvas
        #     canvas = WgpuCanvas(size=(640, 480), title="wgpu_renderer")

        self._canvas = canvas

        self.autoClear = True
        self.autoClearColor = True
        self.autoClearDepth = True
        self.autoClearStencil = True

        self.outputEncoding = LinearEncoding

        self.toneMapping = NoToneMapping
        self.toneMappingExposure = 1.0

        self.sortObjects = True

        # internals

        self._parameters = parameters.copy()

        self._pixelRatio = self._canvas.get_pixel_ratio()
        self._width, self._height = self._canvas.get_logical_size()

        self._drawingBufferWidth, self._drawingBufferHeight = self._canvas.get_physical_size()

        self._viewport = None
        self._scissor = None

        self._adapter = None
        self._device = None
        self._context = None
        self._colorBuffer = None
        self._depthBuffer = None

        self._info = None
        self._properties = None
        self._attributes = None
        self._geometries = None
        self._nodes = None
        self._bindings = None
        self._objects = None
        self._renderPipelines = None
        self._computePipelines = None
        self._renderLists = None
        self._renderStates = None
        self._textures = None
        self._background = None

        self._renderPassDescriptor = None

        self._currentRenderState = None

        self._currentRenderList = None
        self._opaqueSort = None
        self._transparentSort = None

        self._clearAlpha = 1
        self._clearColor = Color( 0x000000 )
        self._clearDepth = 1
        self._clearStencil = 0

        self._renderTarget = None
        
        self._viewPort = None

        # some parameters require default values other than "undefined"

        self._parameters.antialias = ( parameters.antialias == True )

        if self._parameters.antialias == True:
            self._parameters.sampleCount = parameters.sampleCount if parameters.sampleCount is not None else 4
        else:
            self._parameters.sampleCount = 1

        self._parameters.requiredFeatures = parameters.requiredFeatures if parameters.requiredFeatures is not None else []
        self._parameters.requiredLimits = parameters.requiredLimits if parameters.requiredLimits is not None else {}

    def init(self):
        parameters = self._parameters

        # adapterOptions = {
        #     'powerPreference': parameters.powerPreference
        # }

        adapter = wgpu.gpu.request_adapter_sync(
            canvas = self._canvas, power_preference = parameters.powerPreference
        )

        # adapter = await navigator.gpu.requestAdapter( adapterOptions );

        if adapter is None:
            raise Exception('WebGPURenderer: Unable to create WebGPU adapter.')


        if "float32-filterable" not in parameters.requiredFeatures:
            parameters.requiredFeatures.append( "float32-filterable" ) # we add this feature by default

        deviceDescriptor = {
            'required_features': parameters.requiredFeatures,
            'required_limits': parameters.requiredLimits
        }

        # device = await adapter.requestDevice( deviceDescriptor );

        device:wgpu.GPUDevice = adapter.request_device_sync(**deviceDescriptor)

        context:'wgpu.GPUCanvasContext' = parameters.context if parameters.context is not None else self._canvas.get_context()

        # render_texture_format = context.get_preferred_format(device.adapter)

        self._color_format = GPUTextureFormat.BGRA8Unorm

        context.configure( device = device, format = self._color_format, alpha_mode= 'opaque')  # GPUTextureFormat.BGRA8Unorm

        self._adapter = adapter
        self._device = device
        self._context = context

        self._info = WgpuInfo()
        self._properties = WgpuProperties()
        self._attributes = WgpuAttributes( device )
        self._geometries = WgpuGeometries( self._attributes, self._info )
        self._textures = WgpuTextures( device, self._properties, self._info )
        self._objects = WgpuObjects( self._geometries, self._info )
        self._utils = WgpuUtils( self )
        self._nodes = WgpuNodes( self, self._properties )
        self._computePipelines = WgpuComputePipelines( device, self._nodes)
        self._renderPipelines = WgpuRenderPipelines( device, self._nodes, self._utils )
        self._renderPipelines.bindings = WgpuBindings( device, self._info, self._properties, self._textures, self._renderPipelines, self._computePipelines, self._attributes, self._nodes )
        self._bindings = self._renderPipelines.bindings
        self._renderLists =  WgpuRenderLists()
        self._renderStates = WebGPURenderStates()
        self._background = WgpuBackground( self )

        self._renderPassDescriptor = Dict({
            'color_attachments': [ {
                'view': None,
                'store_op': GPUStoreOp.Store
            } ],
            'depth_stencil_attachment': {
                'view': None,
                'depth_store_op': GPUStoreOp.Store,
                'stencil_store_op': GPUStoreOp.Store
            }
        })

        self._setupColorBuffer()
        self._setupDepthBuffer()

        # def on_size_change(event):
        #     self.setSize(event['width'], event['height'], False)

        # self._canvas.add_event_handler(lambda event: self.setSize(event['width'], event['height'], False), 'resize')


    async def init_async(self):
        # TODO async?
        pass

    def setAnimationLoop(self, animationLoop):
        def loop():
            animationLoop()
            if self._renderTarget is None:
                self._canvas.request_draw()

        self._canvas.request_draw(loop)

    def render( self, scene:'three.Scene', camera:'three.Camera' ):

        # @TODO: move this to animation loop?

        cw, ch = self._canvas.get_physical_size()

        if self._drawingBufferWidth != cw or self._drawingBufferHeight != ch:
            if cw == 0 or ch == 0:
                return
            self._drawingBufferWidth = cw
            self._drawingBufferHeight = ch
            self._setupColorBuffer()
            self._setupDepthBuffer()


        self._nodes.updateFrame()
        #

        if scene.autoUpdate:
            scene.updateMatrixWorld()

        if camera.parent is None:
            camera.updateMatrixWorld()

        if self._info.autoReset:
            self._info.reset()

        _projScreenMatrix.multiplyMatrices( camera.projectionMatrix, camera.matrixWorldInverse )
        _frustum.setFromProjectionMatrix( _projScreenMatrix )

        self._currentRenderList = self._renderLists.get( scene, camera )
        self._currentRenderList.init()

        self._currentRenderState = self._renderStates.get( scene, camera )
        self._currentRenderState.init()

        self._projectObject( scene, camera, 0 )

        self._currentRenderList.finish()

        if self.sortObjects == True:
            self._currentRenderList.sort( self._opaqueSort, self._transparentSort )

        # prepare render pass descriptor

        colorAttachment = self._renderPassDescriptor.color_attachments[ 0 ]
        depthStencilAttachment = self._renderPassDescriptor.depth_stencil_attachment

        renderTarget = self._renderTarget

        if renderTarget is not None:

            # @TODO: Support RenderTarget with antialiasing.
            
            renderTargetProperties = self._properties.get( renderTarget )

            colorAttachment.view = renderTargetProperties.colorTextureGPU.create_view()
            depthStencilAttachment.view = renderTargetProperties.depthTextureGPU.create_view()

        else:
            if self._parameters.antialias:
                colorAttachment.view = self._colorBuffer.create_view()

                #GPUTextureView( "", view_id, self._device, None, size)

                colorAttachment.resolve_target = self._context.get_current_texture().create_view()

            else:
                colorAttachment.view = self._context.get_current_texture().create_view()
                colorAttachment.resolve_target = None
            
            depthStencilAttachment.view = self._depthBuffer.create_view()

        self._background.update( self._currentRenderList, scene )
        # start render pass
        device = self._device
        cmd_encoder:wgpu.GPUCommandEncoder = device.create_command_encoder()
        
        passEncoder:wgpu.GPURenderPassEncoder = cmd_encoder.begin_render_pass(**self._renderPassDescriptor)

        # global rasterization settings for all renderable objects

        if self._viewPort is not None:
            vp = self._viewPort
            width = math.floor( vp.width * self._pixelRatio )
            height = math.floor( vp.height * self._pixelRatio )
            passEncoder.set_viewport( vp.x, vp.y, width, height, vp.minDepth, vp.maxDepth )


        sc = self._scissor

        if sc is not None:
            width = math.floor( sc.width * self._pixelRatio )
            height = math.floor( sc.height * self._pixelRatio )
            passEncoder.set_scissor_rect( sc.x, sc.y, width, height )

        # lights node

        lightsNode = self._currentRenderState.getLightsNode()
        # process render lists

        opaqueObjects = self._currentRenderList.opaque
        transparentObjects = self._currentRenderList.transparent

        if len(opaqueObjects)> 0:
            self._renderObjects( opaqueObjects, camera, scene, lightsNode, passEncoder )
        if len(transparentObjects) > 0:
            self._renderObjects( transparentObjects, camera, scene, lightsNode, passEncoder )
        # finish render pass
    
        passEncoder.end()
        device.queue.submit([cmd_encoder.finish()])

        # if renderTarget is None:
        #     if ch !=0 and cw != 0:
        #         self._canvas.request_draw()
        

    def getContext(self):
        return self._context

    def getArrayFromBuffer(self, attribute):
        return self._attributes.getArrayBuffer( attribute )

    def getPixelRatio(self):
        return self._pixelRatio

    def getDrawingBufferSize( self, target ):
        return target.set( self._drawingBufferWidth, self._drawingBufferHeight )


    def getSize( self, target=None ):
        w, h = self._canvas.get_logical_size()
        if target and target.isVector2:
            return target.set(w, h)
        else:
            return (w, h)

    # def setPixelRatio( self, value = 1 ):
    #     self._pixelRatio = value
    #     self.setSize( self._width, self._height, False )

    # def setDrawingBufferSize( self, width, height, pixelRatio ):

    #     self._width = width
    #     self._height = height

    #     self._pixelRatio = pixelRatio

    #     self._canvas.set_logical_size( width, height)

    #     # self.domElement.width = math.floor( width * pixelRatio )
    #     # self.domElement.height = math.floor( height * pixelRatio )

    #     self._configureContext()
    #     self._setupColorBuffer()
    #     self._setupDepthBuffer()

    def setSize( self, width, height ):

        self._width = width
        self._height = height

        self._canvas.set_logical_size( width, height)

        self._drawingBufferWidth, self._drawingBufferHeight = self._canvas.get_physical_size()

        # self._configureContext()
        self._setupColorBuffer()
        self._setupDepthBuffer()

    def setOpaqueSort( self, method ):
        self._opaqueSort = method

    def setTransparentSort( self, method ):
        self._transparentSort = method

    def getScissor( self, target ):
        scissor = self._scissor

        target.x = scissor.x
        target.y = scissor.y
        target.width = scissor.width
        target.height = scissor.height

        return target

    def setScissor( self, x, y, width, height ):

        if x is None:
            self._scissor = None
        else:
            self._scissor = Dict({
                'x': x,
                'y': y,
                'width': width,
                'height': height
            })


    def getViewport( self, target ):
        viewport = self._viewport

        target.x = viewport.x
        target.y = viewport.y
        target.width = viewport.width
        target.height = viewport.height
        target.minDepth = viewport.minDepth
        target.maxDepth = viewport.maxDepth

        return target


    def setViewport(self, x, y, width, height, minDepth = 0, maxDepth = 1):
        if x == None:
            self._viewport = None

        self._viewPort = Dict({
            'x': x,
            'y': y,
            'width': width,
            'height': height,
            'minDepth': minDepth,
            'maxDepth': maxDepth
        })

    def getClearColor( self, target ):
        return target.copy( self._clearColor )

    def setClearColor( self, color, alpha = 1 ):
        self._clearColor.set( color )
        self._clearAlpha = alpha

    def getClearAlpha( self ):
        return self._clearAlpha

    def setClearAlpha( self, alpha ):
        self._clearAlpha = alpha

    def getClearDepth(self):
        return self._clearDepth

    def setClearDepth( self, depth ):
        self._clearDepth = depth

    def getClearStencil(self):
        return self._clearStencil

    def setClearStencil( self, stencil ):
        self._clearStencil = stencil

    def clear(self):
        self._background.clear()

    def dispose(self):

        self._objects.dispose()
        self._properties.dispose()
        self._renderPipelines.dispose()
        self._computePipelines.dispose()
        self._nodes.dispose()
        self._bindings.dispose()
        self._info.dispose()
        self._renderLists.dispose()
        self._renderStates.dispose()
        self._textures.dispose()

    def setRenderTarget( self, renderTarget ):
        self._renderTarget = renderTarget

        if renderTarget is not None:
            self._textures.initRenderTarget( renderTarget )

    def compute( self, *computeNodes ):

        device = self._device
        computePipelines = self._computePipelines

        cmdEncoder:wgpu.GPUCommandEncoder = device.create_command_encoder()

        passEncoder:wgpu.GPUComputePassEncoder = cmdEncoder.begin_compute_pass()

        for computeNode in computeNodes:

            # onInit
            if not computePipelines.has(computeNode):
                computeNode.onInit(renderer=self)

            # pipeline
            pipeline = computePipelines.get(computeNode)
            passEncoder.set_pipeline( pipeline )

            # node
            # self._nodes.update( computeNode )

            # bind group
            bindGroup = self._bindings.get(computeNode).group
            self._bindings.update(computeNode)
            passEncoder.set_bind_group(0, bindGroup, [], 0, 99)
            passEncoder.dispatch_workgroups(computeNode.dispatchCount)

        passEncoder.end()
        device.queue.submit( [ cmdEncoder.finish() ] )

    def getRenderTarget( self ):
        return self._renderTarget

    def _projectObject( self, object:'three.Object3D', camera:'three.Camera', groupOrder ):
        currentRenderList = self._currentRenderList
        currentRenderState = self._currentRenderState
        
        if object.visible == False:
            return

        visible = object.layers.test( camera.layers )
        if visible:
            if object.isGroup:
                groupOrder = object.renderOrder

            elif object.isLOD:
                if object.autoUpdate == True:
                    object.update( camera )

            elif object.isLight:
                currentRenderState.pushLight( object )
                if object.castShadow:
                    # currentRenderState.pushShadow( object );
                    pass

            elif object.isSprite:
                if not object.frustumCulled or _frustum.intersectsSprite( object ):
                    if self.sortObjects == True:
                        _vector3.setFromMatrixPosition( object.matrixWorld ).applyMatrix4( _projScreenMatrix )

                    geometry:'three.Geometry' = object.geometry
                    material:'three.Material' = object.material

                    if material.visible:
                        currentRenderList.push( object, geometry, material, groupOrder, _vector3.z, None )


            elif object.isLineLoop:
                warn( 'THREE.WebGPURenderer: Objects of type THREE.LineLoop are not supported. Please use THREE.Line or THREE.LineSegments.' )

            elif object.isMesh or object.isLine or object.isPoints:
                if not object.frustumCulled or _frustum.intersectsObject( object ):
                    if self.sortObjects == True:
                        _vector3.setFromMatrixPosition( object.matrixWorld ).applyMatrix4( _projScreenMatrix )
                    
                    geometry:'three.Geometry' = object.geometry
                    material:'three.Material' = object.material

                    if isinstance(material, list):
                        groups = geometry.groups
                        for group in groups:
                            groupMaterial = material[ group.materialIndex ]
                            if groupMaterial and groupMaterial.visible:
                                currentRenderList.push( object, geometry, groupMaterial, groupOrder, _vector3.z, group )

                    elif material.visible:
                        currentRenderList.push( object, geometry, material, groupOrder, _vector3.z, None )


        children = object.children
        for c in children:
            self._projectObject( c, camera, groupOrder )


    def _renderObjects( self, renderList, camera:'three.Camera', scene, lightsNode, passEncoder:wgpu.GPURenderPassEncoder ):
        # process renderable objects
        for renderItem in renderList:

            # @TODO: Add support for multiple materials per object. This will require to extract
            # the material from the renderItem object and pass it with its group data to _renderObject().
            object:'three.Object3D' = renderItem.object
            geometry:'three.Geometry' = renderItem.geometry
            material:'three.Material' = renderItem.material
            group:'three.Group' = renderItem.group

            # object.onBeforeRender(self, scene, camera, renderItem.geometry, renderItem.material, renderItem.group)

            # object.modelViewMatrix.multiplyMatrices( camera.matrixWorldInverse, object.matrixWorld )

            # object.normalMatrix.getNormalMatrix( object.modelViewMatrix )
            # self._objects.update( object )
            # objectProperties = self._properties.get( object )

            # objectProperties.lightsNode = lightsNode
            # objectProperties.scene = scene

            if camera.isArrayCamera:
                cameras:'list[three.Camera]' = camera.cameras

                for camera2 in cameras:
                    if object.layers.test( camera2.layers ):
                        vp = camera2.viewport
                        minDepth = 0 if vp.minDepth is None else vp.minDepth
                        maxDepth = 1 if vp.maxDepth is None else vp.maxDepth

                        passEncoder.set_viewport( vp.x, vp.y, vp.width, vp.height, minDepth, maxDepth )

                        # self._nodes.update( object, camera2 )
                        # self._bindings.update( object )
                        # self._renderObject( object, passEncoder )
                        self._renderObject( object, scene, camera2, geometry, material, group, lightsNode, passEncoder )


            else:
                # self._nodes.update( object, camera )
                # self._bindings.update( object )
                # self._renderObject( object, passEncoder )
                self._renderObject( object, scene, camera, geometry, material, group, lightsNode, passEncoder )


    def _renderObject( self, object, scene, camera, geometry, material, group, lightsNode, passEncoder:wgpu.GPURenderPassEncoder ):
        info = self._info

        objectProperties = self._properties.get( object )

        objectProperties.lightsNode = lightsNode
        objectProperties.scene = scene

        #

        object.onBeforeRender( self, scene, camera, geometry, material, group )

        object.modelViewMatrix.multiplyMatrices( camera.matrixWorldInverse, object.matrixWorld )
        object.normalMatrix.getNormalMatrix( object.modelViewMatrix )

        # updates

        self._nodes.update( object, camera )
        self._bindings.update( object )
        self._objects.update( object )

        # pipeline
        renderPipeline = self._renderPipelines.get( object )

        passEncoder.set_pipeline( renderPipeline.pipeline )

        # bind group
        bindGroup = self._bindings.get( object ).group

        passEncoder.set_bind_group( 0, bindGroup, [], 0, 99 )

        # index
        index = self._geometries.getIndex( geometry, material.wireframe == True )

        hasIndex = index is not None

        if hasIndex:
            self._setupIndexBuffer( index, passEncoder )


        # vertex buffers
        self._setupVertexBuffers( geometry.attributes, passEncoder, renderPipeline )

        passEncoder.set_stencil_reference(material.stencilRef)

        # draw

        drawRange = geometry.drawRange
        firstVertex = drawRange.start
        instanceCount = geometry.instanceCount if geometry.isInstancedBufferGeometry else (object.count if object.isInstancedMesh else 1)

        if hasIndex:
            indexCount = drawRange.count if drawRange.count != math.inf else index.count
            passEncoder.draw_indexed( indexCount, instanceCount, firstVertex, 0, 0 )
            info.update( object, indexCount, instanceCount )

        else:
            positionAttribute = geometry.attributes.position
            vertexCount = drawRange.count if drawRange.count != math.inf else positionAttribute.count
            passEncoder.draw( vertexCount, instanceCount, firstVertex, 0 )
            info.update( object, vertexCount, instanceCount )

    def _setupIndexBuffer( self, index, encoder:wgpu.GPURenderPassEncoder ):
        buffer = self._attributes.get( index ).buffer
        indexFormat = GPUIndexFormat.Uint16 if isinstance(index.array, Uint16Array) else GPUIndexFormat.Uint32
        encoder.set_index_buffer( buffer, indexFormat )

    def _setupVertexBuffers( self, geometryAttributes, encoder:wgpu.GPURenderPassEncoder, renderPipeline ):

        shaderAttributes = renderPipeline.shaderAttributes

        for shaderAttribute in shaderAttributes:

            name = shaderAttribute.name
            slot = shaderAttribute.slot

            attribute = geometryAttributes[ name ]

            if attribute:
                buffer = self._attributes.get( attribute ).buffer
                encoder.set_vertex_buffer( slot, buffer )

    def _setupColorBuffer(self):
        device = self._device
        
        if device:
            if self._colorBuffer:
                self._colorBuffer.destroy()

            self._colorBuffer = self._device.create_texture(
                size={
                    'width': max(1, self._drawingBufferWidth),
                    'height': max(1, self._drawingBufferHeight),
                    'depth_or_array_layers': 1
                },
                sample_count = self._parameters.sampleCount,
                format= self._color_format,
                usage= GPUTextureUsage.RENDER_ATTACHMENT
            )

    def _setupDepthBuffer(self):
        device = self._device
        if device:
            if self._depthBuffer:
                self._depthBuffer.destroy()

            self._depthBuffer = self._device.create_texture(
                size={
                    'width': max(1, self._drawingBufferWidth),
                    'height': max(1, self._drawingBufferHeight),
                    'depth_or_array_layers': 1
                },

                sample_count= self._parameters.sampleCount,
                format= GPUTextureFormat.Depth24PlusStencil8,
                usage= GPUTextureUsage.RENDER_ATTACHMENT
            )

    def _configureContext(self):
        device = self._device
        if device:
            self._context.configure(
                device= device,
                format= self._color_format,
                usage= GPUTextureUsage.RENDER_ATTACHMENT,
                alpha_mode='premultiplied'
                # size= {
                #     'width': math.floor( self._width * self._pixelRatio ),
                #     'height': math.floor( self._height * self._pixelRatio ),
                #     'depth_or_array_layers': 1
                # }
            )
