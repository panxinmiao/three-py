import imageio
import numpy as np
import three
from pathlib import Path

_memoryview_format = {
    'e': three.HalfFloatType,
    'f': three.FloatType,
    'B': three.UnsignedByteType,
    'b': three.ByteType,
    'H': three.UnsignedShortType,
    'h': three.ShortType,
    'L': three.UnsignedIntType,
    'l': three.IntType,
}

class Loader:
    # TODO cache
    def __init__(self, path=''):
        self.path = path

    def load(self, name):
        raise NotImplementedError

    def parse(self):
        pass


class ImageLoader(Loader):
    def load(self, name, flip = False):
        data = imageio.imread(Path(self.path) / name, pilmode='RGBA')
        if flip:
            data = np.ascontiguousarray(np.flipud(data))
        image = three.Image(memoryview(
            data), width=data.shape[1], height=data.shape[0])

        return image


class RGBMLoader(ImageLoader):

    def __init__(self, path=''):
        super().__init__(path)
        self.maxRange = 7

    def setMaxRange(self, value):
        self.maxRange = value
        return self

    def load(self, name):
        data:np.ndarray = imageio.imread(Path(self.path) / name, pilmode='RGBA')
        data = data.astype(np.float32)/255
        data = data * data[:, :, 3:4]*self.maxRange
        data[:, :, 3] = 1
        image = three.Image(memoryview(
            data), width=data.shape[1], height=data.shape[0])

        return image


class TextureLoader(Loader):
    def __init__(self, path=''):
        super().__init__(path)
        self._imageLoader = ImageLoader(path)

    @property
    def imageLoader(self):
        return self._imageLoader

    @imageLoader.setter
    def imageLoader(self, value: ImageLoader):
        self._imageLoader = value
        self._imageLoader.path = self._imageLoader.path or self.path

    def load(self, name, flip = False):
        image = self.imageLoader.load(name, flip)
        texture = three.Texture(image)
        texture.needsUpdate = True
        texture.type = _memoryview_format.get(image.data.format)
        return texture


class CubeTextureLoader(TextureLoader):

    def load(self, urls, flip = False):
        images = []
        for url in urls:
            image = self.imageLoader.load(url, flip)
            images.append(image)

        cubeTexture = three.CubeTexture(images)
        cubeTexture.type = _memoryview_format.get(image.data.format)
        cubeTexture.needsUpdate = True

        return cubeTexture