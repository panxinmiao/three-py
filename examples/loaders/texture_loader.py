import imageio
import re
import struct
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

    def load(self, name, flip = False):
        data:np.ndarray = imageio.imread(Path(self.path) / name, pilmode='RGBA')
        data = data.astype(np.float32)/255
        data = data * data[:, :, 3:4]*self.maxRange
        data[:, :, 3] = 1

        if flip:
            data = np.ascontiguousarray(np.flipud(data))
        image = three.Image(memoryview(
            data), width=data.shape[1], height=data.shape[0])

        return image

HDR_NONE = 0x00
HDR_RLE_RGBE_32 = 0x01

class RGBELoader(ImageLoader):

    def __init__(self, path=''):
        super().__init__(path)

    def load(self, name, flip = False):
        filename = Path(self.path) / name
        img = None
        with open(filename, 'rb') as f:
            bufsize = 4096
            filetype = HDR_NONE
            valid = False
            exposure = 1.0

            # Read header section
            while True:
                buf = f.readline(bufsize).decode('ascii')
                if buf[0] == '#' and (buf == '#?RADIANCE\n' or buf == '#?RGBE\n'):
                    valid = True
                else:
                    p = re.compile('FORMAT=(.*)')
                    m = p.match(buf)
                    if m is not None and m.group(1) == '32-bit_rle_rgbe':
                        filetype = HDR_RLE_RGBE_32
                        continue

                    p = re.compile('EXPOSURE=(.*)')
                    m = p.match(buf)
                    if m is not None:
                        exposure = float(m.group(1))
                        continue

                if buf[0] == '\n':
                    # Header section ends
                    break

            if not valid:
                raise Exception('HDR header is invalid!!')

            # Read body section
            width = 0
            height = 0
            buf = f.readline(bufsize).decode()
            p = re.compile('([\-\+]Y) ([0-9]+) ([\-\+]X) ([0-9]+)')
            m = p.match(buf)
            if m is not None and m.group(1) == '-Y' and m.group(3) == '+X':
                width = int(m.group(4))
                height = int(m.group(2))
            else:
                raise Exception('HDR image size is invalid!!')

            # Check byte array is truly RLE or not
            byte_start = f.tell()
            now = ord(f.read(1))
            now2 = ord(f.read(1))
            if now != 0x02 or now2 != 0x02:
                filetype = HDR_NONE
            f.seek(byte_start)

            if filetype == HDR_RLE_RGBE_32:
                # Run length encoded HDR
                tmpdata = np.zeros((width * height * 4), dtype=np.uint8)
                nowy = 0
                while True:
                    now = -1
                    now2 = -1
                    try:
                        now = ord(f.read(1))
                        now2 = ord(f.read(1))
                    except:
                        break

                    if now != 0x02 or now2 != 0x02:
                        break

                    A = ord(f.read(1))
                    B = ord(f.read(1))
                    width = (A << 8) | B

                    nowx = 0
                    nowv = 0
                    while True:
                        if nowx >= width:
                            nowv += 1
                            nowx = 0
                            if nowv == 4:
                                break

                        info = ord(f.read(1))
                        if info <= 128:
                            data = f.read(info)
                            for i in range(info):
                                tmpdata[(nowy * width + nowx) * 4 + nowv] = data[i]
                                nowx += 1
                        else:
                            num = info - 128
                            data = ord(f.read(1))
                            for i in range(num):
                                tmpdata[(nowy * width + nowx) * 4 + nowv] = data
                                nowx += 1

                    nowy += 1

                tmpdata = tmpdata.reshape((height, width, 4))
            else:
                # Non-encoded HDR format
                totsize = width * height * 4
                tmpdata = struct.unpack('B' * totsize, f.read(totsize))
                tmpdata = np.asarray(tmpdata, np.uint8).reshape((height, width, 4))

            expo = np.power(2.0, tmpdata[:,:,3:4] - 128.0) / 255.0
            img = tmpdata * expo
            img[:, :, 3] = 1
            img = img.astype(np.float32)
            # img = np.multiply(tmpdata[:,:,0:3], expo[:,:,np.newaxis])

        if img is None:
            raise Exception('Failed to load file "{0}"'.format(filename))

        if flip:
            img = np.ascontiguousarray(np.flipud(img))

        image = three.Image(memoryview(
            img), width=img.shape[1], height=img.shape[0])

        return image

class TextureLoader(Loader):
    def __init__(self, path='', encoding=three.LinearEncoding):
        super().__init__(path)
        self._imageLoader = ImageLoader(path)
        self._encoding = encoding

    @property
    def imageLoader(self):
        return self._imageLoader

    @imageLoader.setter
    def imageLoader(self, value: ImageLoader):
        self._imageLoader = value
        self._imageLoader.path = self._imageLoader.path or self.path

    def load(self, name, flip=False, encoding=None):
        image = self.imageLoader.load(name, flip)
        texture = three.Texture(image)
        texture.needsUpdate = True
        texture.type = _memoryview_format.get(image.data.format)
        texture.encoding = encoding or self._encoding

        if isinstance(self._imageLoader, (RGBELoader, RGBMLoader)):
            # HDR image
            # set texture properties automatically according to the source type
            # provide a interface in image loader to override these properties?
            texture.magFilter = three.LinearFilter
            texture.minFilter = three.LinearFilter
            texture.encoding = three.LinearEncoding
            texture.type = three.FloatType

        return texture


class CubeTextureLoader(TextureLoader):

    def load(self, urls, flip=False, encoding=None):
        images = []
        for url in urls:
            image = self.imageLoader.load(url, flip)
            images.append(image)

        cubeTexture = three.CubeTexture(images)
        cubeTexture.type = _memoryview_format.get(image.data.format)
        cubeTexture.encoding = encoding or self._encoding
        cubeTexture.needsUpdate = True

        return cubeTexture