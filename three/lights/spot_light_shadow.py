from .light_shadow import LightShadow
from ..camera.perspective_camera import PerspectiveCamera
from ..math import math_utils as MathUtils
class SpotLightShadow(LightShadow):

    isSpotLightShadow = True

    def __init__(self) -> None:
        super().__init__(PerspectiveCamera( 50, 1, 0.5, 500 ))
        self.focus = 1

    def updateMatrices(self, light):
        camera = self.camera

        fov = MathUtils.RAD2DEG * 2 * light.angle * self.focus
        aspect = self.mapSize.width / self.mapSize.height
        far = light.distance or camera.far

        if fov != camera.fov or aspect != camera.aspect or far != camera.far:
            camera.fov = fov
            camera.aspect = aspect
            camera.far = far
            camera.updateProjectionMatrix()

        super().updateMatrices( light )