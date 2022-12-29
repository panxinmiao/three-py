from .light import Light
from .spot_light_shadow import SpotLightShadow
from ..core.object3d import Object3D
import math

class SpotLight(Light):

    isSpotLight = True

    def __init__(self, color, intensity, distance = 0, angle = math.pi / 3, penumbra = 0, decay = 2):
        super().__init__(color, intensity)

        self._type = 'SpotLight'

        self.position.copy(Object3D.DefaultUp)
        self.updateMatrix()

        self.target = Object3D()

        self.distance = distance
        self.angle = angle
        self.penumbra = penumbra
        self.decay = decay

        self.map = None
        self.shadow = SpotLightShadow()

    @property
    def power(self):
        # compute the light's luminous power (in lumens) from its intensity (in candela)
		# by convention for a spotlight, luminous power (lm) = π * luminous intensity (cd)
        return self.intensity * math.pi

    @power.setter
    def power(self, power):
        # set the light's intensity (in candela) from the desired luminous power (in lumens)
        self.intensity = power / math.pi

    def dispose(self):
        self.shadow.dispose()
    
    def copy(self, source: 'SpotLight', recursive=True):
        super().copy(source, recursive)

        self.distance = source.distance
        self.angle = source.angle
        self.penumbra = source.penumbra
        self.decay = source.decay

        self.target = source.target.clone()
        self.shadow = source.shadow.clone()
        return self

