
from .texture import Texture
from ..constants import CubeReflectionMapping

class CubeTexture(Texture):

    def __init__(self, images=None, mapping=CubeReflectionMapping, *args, **kwargs) -> None:
        
        images = images if images else []

        # mapping = mapping if mapping else CubeReflectionMapping

        super().__init__(images, mapping, *args, **kwargs)

        self.flipY = False


    @property
    def images(self):
        return self.image

    @images.setter
    def images(self, value ):
        self.image = value
