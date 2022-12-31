from .light_shadow import LightShadow
from ..camera.orthographic_camera import OrthographicCamera

class DirectionalLightShadow(LightShadow):

    isDirectionalLightShadow = True

    def __init__(self) -> None:
        super().__init__(OrthographicCamera( -5, 5, 5, -5, 0.5, 500 ))