from ...structure import Dict

class WgpuProgrammableStage:

    _id = 0

    def __init__(self,device, code, type) -> None:
        
        self.id = WgpuProgrammableStage._id
        WgpuProgrammableStage._id += 1

        self.code = code
        self.type = type
        self.usedTimes = 0

        self.stage = Dict({
			'module': device.create_shader_module( code = code ),
			'entry_point': 'main'
		})
