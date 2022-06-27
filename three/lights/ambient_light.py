from .light import Light

class AmbientLight(Light):

    isAmbientLight = True

    def __init__(self, color, intensity=1):
        super().__init__(color, intensity)
        self._type = 'AmbientLight'