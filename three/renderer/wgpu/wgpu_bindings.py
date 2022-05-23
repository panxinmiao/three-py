from weakref import WeakKeyDictionary
import wgpu
from ...structure import Dict

class WgpuBindings:

    def __init__(self, device, info, properties, textures, renderPipelines, computePipelines, attributes, nodes ) -> None:
        
        self.device: wgpu.GPUDevice = device
        self.info = info
        self.properties = properties
        self.textures = textures
        self.renderPipelines = renderPipelines
        self.computePipelines = computePipelines
        self.attributes = attributes
        self.nodes = nodes

        self.uniformsData = WeakKeyDictionary()

        self.updateMap = WeakKeyDictionary()


    def get( self, object ):
        data = self.uniformsData.get( object )
        if data is None:
            
            # each object defines an array of bindings (ubos, textures, samplers etc.)
            nodeBuilder = self.nodes.get( object )
            bindings = nodeBuilder.getBindings()
            # setup (static) binding layout and (dynamic) binding group
            # renderPipeline = self.renderPipelines.get( object )
            
            pipeline = self.computePipelines.get(
                object) if object.isNode else self.renderPipelines.get(object).pipeline

            bindLayout = pipeline.get_bind_group_layout( 0 )
            bindGroup = self._createBindGroup( bindings, bindLayout )

            data = Dict({
				'layout': bindLayout,
				'group': bindGroup,
				'bindings': bindings
			})
            self.uniformsData[object] = data

        return data

    def remove( self, object ):
        self.uniformsData.pop( object )


    def getForCompute( self, param ):
        data = self.uniformsData.get( param )
        
        if data is None:

            # bindings are not yet retrieved via node material
            bindings =  param.bindings[:] if param.bindings else []

            computePipeline = self.computePipelines.get( param )

            bindLayout = computePipeline.get_bind_group_layout( 0 )
            bindGroup = self._createBindGroup( bindings, bindLayout )

            data = Dict({
				'layout': bindLayout,
				'group': bindGroup,
				'bindings': bindings
			})

        self.uniformsData[param] = data

        return data

    
    def update( self, object ):
        textures = self.textures
        data = self.get( object )
        bindings = data['bindings']
        updateMap = self.updateMap
        frame = self.info.render.frame

        needsBindGroupRefresh = False

        # iterate over all bindings and check if buffer updates or a new binding group is required

        for binding in bindings:
            isShared = binding.isShared
            isUpdated = updateMap.get( binding ) == frame
            if isShared and isUpdated:
                continue

            if binding.isUniformBuffer:
                buffer = binding.getBuffer()
                needsBufferWrite = binding.update()

                if needsBufferWrite:
                    bufferGPU = binding.bufferGPU
                    self.device.queue.write_buffer( bufferGPU, 0, buffer.range_buffer(), 0 )


            elif binding.isStorageBuffer:
                attribute = binding.attribute
                self.attributes.update( attribute, False, binding.usage )

            elif binding.isSampler:
                texture = binding.getTexture()

                textures.updateSampler( texture )

                samplerGPU = textures.getSampler( texture )

                if binding.samplerGPU != samplerGPU:
                    binding.samplerGPU = samplerGPU
                    needsBindGroupRefresh = True

            elif binding.isSampledTexture:
                
                texture = binding.getTexture()

                needsTextureRefresh = textures.updateTexture( texture )
                textureGPU = textures.getTextureGPU( texture )

                if textureGPU and binding.textureGPU != textureGPU or needsTextureRefresh :
                    binding.textureGPU = textureGPU
                    needsBindGroupRefresh = True

            updateMap[binding] = frame

        if needsBindGroupRefresh:
            data['group'] = self._createBindGroup( bindings, data['layout'] )

        
    def dispose(self):
        self.uniformsData = WeakKeyDictionary()
        self.updateMap = WeakKeyDictionary()


    def _createBindGroup( self, bindings, layout ):

        bindingPoint = 0
        entries = []

        for binding in bindings:
            if binding.isUniformBuffer:
                if binding.bufferGPU is None:
                    byteLength = binding.getByteLength()
                    
                    binding.bufferGPU = self.device.create_buffer(
						size = byteLength,
						usage = binding.usage
					)
                entries.append( { 'binding': bindingPoint, 'resource': { 'buffer': binding.bufferGPU, "offset": 0, 'size': binding.getByteLength()} } )

            elif binding.isStorageBuffer:
                if binding.bufferGPU is None:
                    attribute = binding.attribute

                    self.attributes.update( attribute, False, binding.usage )
                    binding.bufferGPU = self.attributes.get( attribute ).buffer

                entries.append( { 'binding': bindingPoint, 'resource': { 'buffer': binding.bufferGPU, "offset": 0, 'size':binding.getByteLength()} } )

            elif binding.isSampler:

                if binding.samplerGPU is None:
                    binding.samplerGPU = self.textures.getDefaultSampler()
                
                entries.append( { 'binding': bindingPoint, 'resource': binding.samplerGPU } )

            elif binding.isSampledTexture:

                if binding.textureGPU is None:
                    if binding.isSampledCubeTexture:
                        binding.textureGPU = self.textures.getDefaultCubeTexture()
                    else:
                        binding.textureGPU = self.textures.getDefaultTexture()

                entries.append( { 'binding': bindingPoint, 'resource': binding.textureGPU.create_view( dimension = binding.dimension ) } )

	
            bindingPoint += 1


        return self.device.create_bind_group(
			layout = layout,
			entries = entries
		)

