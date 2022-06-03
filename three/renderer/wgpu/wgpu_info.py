from ...structure import Dict
import warnings

class WgpuInfo:

    def __init__(self) -> None:
        self.autoReset = True

        self.render = Dict({
            'frame': 0,
            'drawCalls': 0,
            'triangles': 0,
            'points': 0,
            'lines': 0
        })

        self.memory = Dict({
            'geometries': 0,
            'textures': 0
        })

    def update( self, object, count, instanceCount ):

        self.render.drawCalls += 1

        if object.isMesh:
            self.render.triangles += instanceCount * ( count / 3 )

        elif object.isPoints:
            self.render.points += instanceCount * count

        elif object.isLineSegments:
            self.render.lines += instanceCount * ( count / 2 )

        elif object.isLine:
            self.render.lines += instanceCount * ( count - 1 )

        else:
            warnings.warn( 'THREE.WebGPUInfo: Unknown object type.' )

    def reset(self):

        self.render.frame += 1
        self.render.drawCalls = 0
        self.render.triangles = 0
        self.render.points = 0
        self.render.lines = 0


    def dispose(self):
        self.reset()
        self.render.frame = 0
        self.memory.geometries = 0
        self.memory.textures = 0


