from math import floor, ceil
from .math_utils import clamp
import three
from ..structure import NoneAttribute

class Vector2(NoneAttribute):
    def __init__(self, x: float = 0, y: float = 0) -> None:
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"Vector2({self.x}, {self.y})"

    @property    
    def width(self):
        return self.x

    @width.setter
    def width(self, value):
        self.x = value

    @property
    def height(self):
        return self.y

    @height.setter
    def height( self, value):
        self.y = value

    def set(self, x: float, y: float) -> "Vector2":
        self.x = x
        self.y = y
        return self

    def setScalar(self, s: float) -> "Vector2":
        self.x = s
        self.y = s
        return self

    def setX(self, x: float) -> "Vector2":
        self.x = x
        return self

    def setY(self, y: float) -> "Vector2":
        self.y = y
        return self

    def setComponent(self, index: int, value: float) -> "Vector2":
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value
        else:
            raise IndexError()
        return self

    def getComponent(self, index: int) -> float:
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError()

    def clone(self) -> "Vector2":
        return Vector2(self.x, self.y)

    def copy(self, v: "Vector2") -> "Vector2":
        self.x = v.x
        self.y = v.y
        return self

    def add(self, v: "Vector2") -> "Vector2":
        self.x += v.x
        self.y += v.y
        return self

    def addScalar(self, s: float) -> "Vector2":
        self.x += s
        self.y += s
        return self

    def addVectors(self, a: "Vector2", b: "Vector2") -> "Vector2":
        self.x = a.x + b.x
        self.y = a.y + b.y
        return self

    def addScaledVector(self, v: "Vector2", s: float) -> "Vector2":
        self.x += v.x * s
        self.y += v.y * s
        return self

    def sub(self, v: "Vector2") -> "Vector2":
        self.x -= v.x
        self.y -= v.y
        return self

    def subScalar(self, s: float) -> "Vector2":
        self.x -= s
        self.y -= s
        return self

    def subVectors(self, a: "Vector2", b: "Vector2") -> "Vector2":
        self.x = a.x - b.x
        self.y = a.y - b.y
        return self

    def multiply(self, v: "Vector2") -> "Vector2":
        self.x *= v.x
        self.y *= v.y
        return self

    def multiplyScalar(self, s: float) -> "Vector2":
        self.x *= s
        self.y *= s
        return self

    def multiplyVectors(self, a: "Vector2", b: "Vector2") -> "Vector2":
        self.x = a.x * b.x
        self.y = a.y * b.y
        return self

    def divide(self, v: "Vector2") -> "Vector2":
        self.x /= v.x
        self.y /= v.y
        return self

    def divideScalar(self, s: float) -> "Vector2":
        self.x /= s
        self.y /= s
        return self

    def applyMatrix3( self, m: 'three.Matrix3' ):

        x = self.x
        y = self.y
        e = m.elements

        self.x = e[ 0 ] * x + e[ 3 ] * y + e[ 6 ]
        self.y = e[ 1 ] * x + e[ 4 ] * y + e[ 7 ]

        return self


    def min(self, v: "Vector2") -> "Vector2":
        self.x = min(self.x, v.x)
        self.y = min(self.y, v.y)
        return self

    def max(self, v: "Vector2") -> "Vector2":
        self.x = max(self.x, v.x)
        self.y = max(self.y, v.y)
        return self

    def clamp(self, min: "Vector2", max: "Vector2") -> "Vector2":
        # assumes min < max, component-wise
        self.x = clamp(self.x, min.x, max.x)
        self.y = clamp(self.y, min.y, max.y)
        return self

    def clampScalar(self, min: float, max: float) -> "Vector2":
        self.x = clamp(self.x, min, max)
        self.y = clamp(self.y, min, max)

    def clampLength(self, min: float, max: float) -> "Vector2":
        length = self.length()
        return self.divideScalar(length or 1).multiplyScalar(clamp(length, min, max))

    def floor(self) -> "Vector2":
        self.x = floor(self.x)
        self.y = floor(self.y)
        return self

    def ceil(self) -> "Vector2":
        self.x = ceil(self.x)
        self.y = ceil(self.y)
        return self

    def round(self) -> "Vector2":
        self.x = round(self.x)
        self.y = round(self.y)
        return self

    def roundToZero(self) -> "Vector2":
        self.x = ceil(self.x) if self.x < 0 else floor(self.x)
        self.y = ceil(self.y) if self.y < 0 else floor(self.y)
        return self

    def negate(self) -> "Vector2":
        self.x = -self.x
        self.y = -self.y
        return self

    def dot(self, v: "Vector2") -> float:
        return self.x * v.x + self.y * v.y

    def lengthSq(self) -> float:
        return self.x ** 2 + self.y ** 2

    def length(self) -> float:
        return self.lengthSq() ** 0.5

    def manhattanLength(self) -> float:
        return abs(self.x) + abs(self.y)

    def normalize(self) -> "Vector2":
        return self.divideScalar(self.length() or 1)

    def setLength(self, length: float) -> "Vector2":
        return self.normalize().multiplyScalar(length)

    def lerp(self, v: "Vector2", a: float) -> "Vector2":
        self.x += (v.x - self.x) * a
        self.y += (v.y - self.y) * a
        return self

    def lerpVectors(self, v1: "Vector2", v2: "Vector2", a: float) -> "Vector2":
        return self.subVectors(v2, v1).multiplyScalar(a).add(v1)

    def cross(self, v: "Vector2") -> "Vector2":
        return self.x * v.y - self.y * v.x

    def distanceTo(self, v: "Vector2") -> float:
        return self.distanceToSquared(v) ** 0.5

    def distanceToSquared(self, v: "Vector2") -> float:
        dx = self.x - v.x
        dy = self.y - v.y

        return dx * dx + dy * dy

    def manhattanDistanceTo(self, v: "Vector2") -> float:
        return abs(self.x - v.x) + abs(self.y - v.y)

    def equals(self, v: "Vector2") -> bool:
        return self.x == v.x and self.y == v.y

    def __eq__(self, other: "Vector2") -> bool:
        return isinstance(other, Vector2) and self.equals(other)

    def fromArray(self, array: list, offset: int = 0) -> "Vector2":
        self.x = array[offset]
        self.y = array[offset + 1]
        return self

    def toArray(self, array: list = None, offset: int = 0) -> list:
        if array is None:
            array = []

        padding = offset + 2 - len(array)
        if padding > 0:
            array.extend((None for _ in range(padding)))

        array[offset] = self.x
        array[offset + 1] = self.y
        return array

    def fromBufferAttribute(self, attribute:'three.BufferAttribute', index: int) -> 'Vector2':
        self.x = attribute.getX( index )
        self.y = attribute.getY( index )
        return self
    

    @property
    def isVector2(self):
        return True
