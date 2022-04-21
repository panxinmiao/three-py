from ..core import Object3D

class Scene(Object3D):
    def __init__(self, name=''):
        super().__init__(name = name)
        self._type = 'Scene'
        self.background = None
        self.autoUpdate = True

    @property
    def isScene(self):
        return True