from ..structure import NoneAttribute
from ..math.color import Color

class FogExp2(NoneAttribute):

    isFogExp2 = True

    def __init__(self, color, density = 0.00025) -> None:
        
        self.color = Color( color )
        self.density = density

    def clone(self):
        return FogExp2(self.color, self.density)