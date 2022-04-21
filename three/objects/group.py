
from ..core import Object3D

class Group(Object3D):
    def __init__(self, name=''):
        super().__init__(name = name)
        self._type = 'Group'

    @property
    def isGroup(self):
        return True