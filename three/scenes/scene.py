from ..core import Object3D

class Scene(Object3D):

    isScene = True

    def __init__(self, name=''):
        super().__init__(name = name)
        self._type = 'Scene'
        self.background = None
        self.environment = None
        self.fog = None

        self.autoUpdate = True