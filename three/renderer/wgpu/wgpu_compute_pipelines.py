import os
from weakref import WeakKeyDictionary
from ...structure import Dict
from .wgpu_programmable_stage import WgpuProgrammableStage
import wgpu

class WgpuComputePipelines:

    def __init__(self, device: wgpu.GPUDevice, nodes) -> None:
        self.device = device
        self.nodes = nodes
        self.pipelines = WeakKeyDictionary()
        self.stages = Dict({
			'compute': {}
		})

    def get(self, computeNode):

        pipeline = self.pipelines.get(computeNode)

        # @TODO: Reuse compute pipeline if possible, introduce WebGPUComputePipeline

        if pipeline is None:
            device = self.device

            nodeBuilder = self.nodes.get(computeNode)
            computeShader = nodeBuilder.computeShader
            
            if os.getenv('SHOW_WGSL') == 'on':
                print('\n===============Stage Compute=================\n', computeShader)
            # programmable stage
            stageCompute = self.stages.compute.get(computeShader)

            if stageCompute is None:
                stageCompute = WgpuProgrammableStage( device, computeShader, 'compute' )
                self.stages.compute.__setitem__(computeShader, stageCompute)

            bindings = nodeBuilder.getBindings()

            _layout = self._getPeplineLayout(bindings)

            pipeline = device.create_compute_pipeline(
                layout=_layout,
				compute = stageCompute.stage
            )

            self.pipelines[computeNode]=pipeline

        return pipeline

    def dispose(self):
        self.pipelines = WeakKeyDictionary()
        self.stages = Dict({
			'compute': WeakKeyDictionary()
		})

    def _getPeplineLayout(self, bindings):
        bind_group_layouts = []

        bindingPoint = 0
        entries = []

        for binding in bindings:
            if binding.isUniformBuffer:
                entries.append({
                    'binding': bindingPoint,
                    'visibility': binding.visibility,
                    "buffer": {
                        "type": 'uniform',
                        "has_dynamic_offset": False,
                        "min_binding_size": 0,
                    }
                })

            elif binding.isStorageBuffer:
                entries.append({
                    'binding': bindingPoint,
                    'visibility': binding.visibility,
                    "buffer": {
                        "type": 'storage',
                        "has_dynamic_offset": False,
                        "min_binding_size": 0,
                    }
                })

            elif binding.isSampler:
                entries.append({
                    'binding': bindingPoint,
                    'visibility': binding.visibility,
                    "sampler": {
                        "type": binding.type
                    }
                })

            elif binding.isSampledTexture:
                entries.append({
                    'binding': bindingPoint,
                    'visibility': binding.visibility,
                    "texture": {
                        "type": binding.type
                    }
                })

            bindingPoint += 1

        bind_group_layout = self.device.create_bind_group_layout(
            entries=entries)
        bind_group_layouts.append(bind_group_layout)
        peppeline_layout = self.device.create_pipeline_layout(
            bind_group_layouts=bind_group_layouts)
        return peppeline_layout
