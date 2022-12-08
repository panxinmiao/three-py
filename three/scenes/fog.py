from ..structure import NoneAttribute
from ..math.color import Color

class Fog(NoneAttribute):

    isFog = True

    def __init__(self, color, near = 1, far = 1000) -> None:
        self.color = Color( color )

        self.near = near
        self.far = far
    
    def clone(self):
        return Fog(self.color, self.near, self.far)