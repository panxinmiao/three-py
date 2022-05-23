from .wgpu_render_pipeline import WgpuRenderPipeline
from .wgpu_programmable_stage import WgpuProgrammableStage
from weakref import WeakKeyDictionary
from ...structure import Dict
import os

class WgpuRenderPipelines:

    def __init__(self, renderer, device, sampleCount, nodes, bindings = None) -> None:
        
        self.renderer = renderer
        self.device = device
        self.sampleCount = sampleCount
        self.nodes = nodes
        self.bindings = bindings

        self.pipelines = []
        self.objectCache = WeakKeyDictionary()

        self.stages = Dict({
            'vertex': {},
            'fragment': {}
        })

    def get( self, object ):
        device = self.device

        cache = self._getCache( object )

        currentPipeline = None

        if self._needsUpdate( object, cache ):
            material = object.material
            
            # release previous cache
            if cache.currentPipeline:
                self._releaseObject( object )

            # get shader

            nodeBuilder = self.nodes.get( object )
            
            # programmable stages
            if os.getenv('SHOW_WGSL') == 'on':
                print('\n===============Stage Vertex=================\n', nodeBuilder.vertexShader)
                print('\n===============Stage Fragment=================\n', nodeBuilder.fragmentShader)

            stageVertex = self.stages.vertex.get( nodeBuilder.vertexShader )
            if stageVertex is None:
                stageVertex = WgpuProgrammableStage( device, nodeBuilder.vertexShader, 'vertex' )
                self.stages.vertex.__setitem__( nodeBuilder.vertexShader, stageVertex )

            stageFragment = self.stages.fragment.get( nodeBuilder.fragmentShader )
            if stageFragment is None:
                stageFragment = WgpuProgrammableStage( device, nodeBuilder.fragmentShader, 'fragment' )
                self.stages.fragment.__setitem__( nodeBuilder.fragmentShader, stageFragment )
            
            # determine render pipeline
            currentPipeline = self._acquirePipeline( stageVertex, stageFragment, object, nodeBuilder )
            cache.currentPipeline = currentPipeline

            # keep track of all used times
            
            currentPipeline.usedTimes += 1
            stageVertex.usedTimes += 1
            stageFragment.usedTimes += 1

            # events

            material.addEventListener( 'dispose', cache.dispose )

        else:
            currentPipeline = cache.currentPipeline

        return currentPipeline

    def dispose( self ):
        self.pipelines = []
        self.objectCache = WeakKeyDictionary()
        self.shaderModules = {
			'vertex': {},
			'fragment': {}
		}

    def _acquirePipeline( self, stageVertex, stageFragment, object, nodeBuilder ):
        pipelines = self.pipelines

        # check for existing pipeline

        cacheKey = self._computeCacheKey( stageVertex, stageFragment, object )

        pipeline = None

        for preexistingPipeline in pipelines:
            if preexistingPipeline.cacheKey == cacheKey:
                pipeline = preexistingPipeline
                break

        
        if pipeline is None:
            pipeline = WgpuRenderPipeline( self.device, self.renderer, self.sampleCount )
            pipeline.init( cacheKey, stageVertex, stageFragment, object, nodeBuilder )
            pipelines.append( pipeline )

        return pipeline

    def _computeCacheKey( self, stageVertex, stageFragment, object ):

        material = object.material
        renderer = self.renderer

        parameters = [
            stageVertex.id, stageFragment.id,
            material.transparent, material.blending, material.premultipliedAlpha,
            material.blendSrc, material.blendDst, material.blendEquation,
            material.blendSrcAlpha, material.blendDstAlpha, material.blendEquationAlpha,
            material.colorWrite,
            material.depthWrite, material.depthTest, material.depthFunc,
            material.stencilWrite, material.stencilFunc,
            material.stencilFail, material.stencilZFail, material.stencilZPass,
            material.stencilFuncMask, material.stencilWriteMask,
            material.side,
            self.sampleCount,
            renderer.getCurrentEncoding(), renderer.getCurrentColorFormat(), renderer.getCurrentDepthStencilFormat()
        ]

        return ','.join( [ str(e) for e in parameters] )
        # return parameters.join()


    def _getCache( self, object ):

        cache = self.objectCache.get( object )

        if cache is None:

            def _dispose():
                self._releaseObject( object )
                self.objectCache.__delitem__( object )
                object.material.removeEventListener( 'dispose', cache.dispose )

            cache = Dict({
                'dispose': _dispose
            })

            self.objectCache.__setitem__( object, cache )

        return cache

    def _releaseObject( self, object ):
        cache = self.objectCache.get( object )
        self._releasePipeline( cache.currentPipeline )
        del cache.currentPipeline
        
        self.nodes.remove( object )
        self.bindings.remove( object )

    def _releasePipeline( self, pipeline ):

        pipeline.usedTimes -= 1
        
        if pipeline.usedTimes == 0:
            pipelines = self.pipelines

            i = pipelines.index( pipeline )
            pipelines[ i ] = pipelines[ pipelines.length - 1 ]
            pipelines.pop()
            self._releaseStage( pipeline.stageVertex )
            self._releaseStage( pipeline.stageFragment )

    def _releaseStage( self, stage ):
        stage.usedTimes -= 1
        
        if stage.usedTimes == 0:
            code = stage.code
            type = stage.type
            self.stages[ type ].pop( code, None )

    
    def _needsUpdate( self, object, cache ):

        material = object.material

        needsUpdate = False

        # check material state

        if (cache.material != material or cache.materialVersion != material.version or
            cache.transparent != material.transparent or cache.blending != material.blending or cache.premultipliedAlpha != material.premultipliedAlpha or
            cache.blendSrc != material.blendSrc or cache.blendDst != material.blendDst or cache.blendEquation != material.blendEquation or
            cache.blendSrcAlpha != material.blendSrcAlpha or cache.blendDstAlpha != material.blendDstAlpha or cache.blendEquationAlpha != material.blendEquationAlpha or
            cache.colorWrite != material.colorWrite or
            cache.depthWrite != material.depthWrite or cache.depthTest != material.depthTest or cache.depthFunc != material.depthFunc or
            cache.stencilWrite != material.stencilWrite or cache.stencilFunc != material.stencilFunc or
            cache.stencilFail != material.stencilFail or cache.stencilZFail != material.stencilZFail or cache.stencilZPass != material.stencilZPass or
            cache.stencilFuncMask != material.stencilFuncMask or cache.stencilWriteMask != material.stencilWriteMask or
            cache.side != material.side
        ):

            cache.material = material; cache.materialVersion = material.version
            cache.transparent = material.transparent; cache.blending = material.blending; cache.premultipliedAlpha = material.premultipliedAlpha
            cache.blendSrc = material.blendSrc; cache.blendDst = material.blendDst; cache.blendEquation = material.blendEquation
            cache.blendSrcAlpha = material.blendSrcAlpha; cache.blendDstAlpha = material.blendDstAlpha; cache.blendEquationAlpha = material.blendEquationAlpha
            cache.colorWrite = material.colorWrite
            cache.depthWrite = material.depthWrite; cache.depthTest = material.depthTest; cache.depthFunc = material.depthFunc
            cache.stencilWrite = material.stencilWrite; cache.stencilFunc = material.stencilFunc
            cache.stencilFail = material.stencilFail; cache.stencilZFail = material.stencilZFail; cache.stencilZPass = material.stencilZPass
            cache.stencilFuncMask = material.stencilFuncMask; cache.stencilWriteMask = material.stencilWriteMask
            cache.side = material.side

            needsUpdate = True

        # check renderer state

        renderer = self.renderer

        encoding = renderer.getCurrentEncoding()
        colorFormat = renderer.getCurrentColorFormat()
        depthStencilFormat = renderer.getCurrentDepthStencilFormat()

        if ( cache.sampleCount != self.sampleCount or cache.encoding != encoding or
            cache.colorFormat != colorFormat or cache.depthStencilFormat != depthStencilFormat ):

            cache.sampleCount = self.sampleCount
            cache.encoding = encoding
            cache.colorFormat = colorFormat
            cache.depthStencilFormat = depthStencilFormat

            needsUpdate = True

        return needsUpdate
