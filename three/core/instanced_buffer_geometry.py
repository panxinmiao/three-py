import math
from .geometry import Geometry

class InstancedGeometry(Geometry):

    def __init__(self) -> None:
        super().__init__()

        self.instanceCount = math.inf

    def copy(self, source: 'InstancedGeometry') -> 'InstancedGeometry':
        super().copy(source)
        self.instanceCount = source.instanceCount
        return self

    def clone(self):
        return self.__class__().copy(self)
