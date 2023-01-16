from .texture import Texture
from .image import Image
from ..constants import NearestFilter, ClampToEdgeWrapping

class Data3DTexture(Texture):

    isData3DTexture = True

    def __init__(self, data=None, width = 1, height = 1, depth = 1) -> None:
        super().__init__(None)

        self.image = Image(data, width, height, depth)

        self.magFilter = NearestFilter
        self.minFilter = NearestFilter

        self.wrapR = ClampToEdgeWrapping

        self.generateMipmaps = False
        self.flipY = False
        self.unpackAlignment = 1
