from ..core import Object3D, BufferGeometry, InterleavedBuffer, InterleavedBufferAttribute
from ..math import Vector2, Vector3, Matrix4, Triangle
from ..structure import Float32Array
from ..materials import SpriteMaterial


class Sprite(Object3D):

    isSprite = True

    _geometry = None

    def __init__(self, material):
        super().__init__()

        self._type = 'Sprite'

        if Sprite._geometry is None:
            Sprite._geometry = BufferGeometry()

            float32Array = Float32Array([
                - 0.5, - 0.5, 0, 0, 0,
                0.5, - 0.5, 0, 1, 0,
                0.5, 0.5, 0, 1, 1,
                - 0.5, 0.5, 0, 0, 1
            ])

            interleavedBuffer = InterleavedBuffer(float32Array, 5)

            Sprite._geometry.setIndex([0, 1, 2, 0, 2, 3])
            Sprite._geometry.setAttribute('position', InterleavedBufferAttribute(interleavedBuffer, 3, 0, False))
            Sprite._geometry.setAttribute('uv', InterleavedBufferAttribute(interleavedBuffer, 2, 3, False))

        self.geometry = Sprite._geometry
        self.material = material or SpriteMaterial()

        self.center =  Vector2(0.5, 0.5)

    def raycast(self, raycaster, intersects):
        raise NotImplementedError()

    def copy(self, source, recursive):
        super().copy(source, recursive)

        if source.center:
            self.center.copy(source.center)

        self.material = source.material
        return self

