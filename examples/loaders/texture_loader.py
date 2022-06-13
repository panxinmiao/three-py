from json import load
import imageio
import three
from pathlib import Path

class TextureLoader:

    def __init__(self, path = None):
        self.path = path or '.'

    def load(self, name):
        data = imageio.imread(Path(self.path) / name)

        image = three.Image(memoryview(
            data), width=data.shape[1], height=data.shape[0])

        tex = three.Texture(image)
        tex.needsUpdate = True

        return tex

setattr(three, 'TextureLoader', TextureLoader)


if __name__ == '__main__':
    loader = TextureLoader(Path(__file__).parent.parent / "textures")

    tex = loader.load('sprite1.png')

    print(tex)