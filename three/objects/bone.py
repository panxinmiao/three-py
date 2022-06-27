from ..core import Object3D

class Bone(Object3D):

    isBone = True

    def __init__(self, name=''):
        super().__init__(name = name)
        self._type = 'Bone'

    def __repr__(self) -> str:
        return f'Bone {self.name} {self.position} {self.rotation}\n'