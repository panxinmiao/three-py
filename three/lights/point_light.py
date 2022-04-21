from .light import Light
from .point_light_shadow import PointLightShadow
import math

class PointLight(Light):
    def __init__(self, color, intensity=1, distance = 0, decay = 1):
        super().__init__(color, intensity)

        self._type = 'PointLight'

        self.distance = distance
        self.decay = decay; # for physically correct lights, should be 2.

        self.shadow = PointLightShadow()

    @property
    def power( self ):

        # compute the light's luminous power (in lumens) from its intensity (in candela)
        # for an isotropic light source, luminous power (lm) = 4 π luminous intensity (cd)
        return self.intensity * 4 * math.pi

    @power.setter
    def power( self, power ):
        # set the light's intensity (in candela) from the desired luminous power (in lumens)
        self.intensity = power / ( 4 * math.pi )


    def dispose(self):
        self.shadow.dispose()

    def copy( self, source:'PointLight' ):
        super().copy( source )
        self.distance = source.distance
        self.decay = source.decay
        self.shadow = source.shadow.clone()

        return self