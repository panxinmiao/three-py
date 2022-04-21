from weakref import WeakKeyDictionary
from ...structure import Dict
from .wgpu_programmable_stage import WgpuProgrammableStage
import wgpu

class WgpuComputePipelines:

    def __init__(self, device: wgpu.GPUDevice) -> None:
        self.device = device
        self.pipelines = WeakKeyDictionary()
        self.stages = Dict({
			'compute': WeakKeyDictionary()
		})

    def get( self, param ):

        pipeline = self.pipelines.get( param )

        # @TODO: Reuse compute pipeline if possible, introduce WebGPUComputePipeline

        if pipeline is None:
            device = self.device
            
            shader = {
				'computeShader': param.shader
			}

            # programmable stage

            stageCompute = self.stages.compute.get( shader )

            if stageCompute is None:
                stageCompute = WgpuProgrammableStage( device, shader['computeShader'], 'compute' )
                self.stages.compute.set( shader, stageCompute )


            pipeline = device.create_compute_pipeline(
				compute = stageCompute.stage
            )

            self.pipelines.set( param, pipeline )

        return pipeline

    def dispose(self):
        self.pipelines = WeakKeyDictionary()
        self.stages = Dict({
			'compute': WeakKeyDictionary()
		})
