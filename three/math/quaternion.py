from math import cos, sin, acos, atan2, pi

from .math_utils import clamp, MACHINE_EPSILON
from ..structure import NoneAttribute

import three

class Quaternion(NoneAttribute):
    def __init__(self, x: float = 0, y: float = 0, z: float = 0, w: float = 1) -> None:
        self._x = x
        self._y = y
        self._z = z
        self._w = w

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value
        self._onChangeCallback()

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value
        self._onChangeCallback()

    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, value):
        self._z = value
        self._onChangeCallback()

    @property
    def w(self):
        return self._w

    @w.setter
    def w(self, value):
        self._w = value
        self._onChangeCallback()
    
    def set(self, x: float, y: float, z: float, w: float) -> "Quaternion":
        self._x = x
        self._y = y
        self._z = z
        self._w = w
        self._onChangeCallback()
        return self

    def clone(self) -> "Quaternion":
        return Quaternion(self._x, self._y, self._z, self._w)

    def __repr__(self) -> str:
        return f"Quaternion({self._x}, {self._y}, {self._z}, {self._w})"

    def copy(self, quaternion: "Quaternion") -> "Quaternion":
        self._x = quaternion.x
        self._y = quaternion.y
        self._z = quaternion.z
        self._w = quaternion.w
        self._onChangeCallback()
        return self

    def setFromEuler(self, euler: "three.Euler", update = True) -> "Quaternion":
        from .euler import Euler

        x = euler._x
        y = euler._y
        z = euler._z
        order = euler._order

        c1 = cos(x / 2)
        c2 = cos(y / 2)
        c3 = cos(z / 2)
        s1 = sin(x / 2)
        s2 = sin(y / 2)
        s3 = sin(z / 2)

        if order == Euler.RotationOrders.XYZ:
            self._x = s1 * c2 * c3 + c1 * s2 * s3
            self._y = c1 * s2 * c3 - s1 * c2 * s3
            self._z = c1 * c2 * s3 + s1 * s2 * c3
            self._w = c1 * c2 * c3 - s1 * s2 * s3
        elif order == Euler.RotationOrders.YXZ:
            self._x = s1 * c2 * c3 + c1 * s2 * s3
            self._y = c1 * s2 * c3 - s1 * c2 * s3
            self._z = c1 * c2 * s3 - s1 * s2 * c3
            self._w = c1 * c2 * c3 + s1 * s2 * s3
        elif order == Euler.RotationOrders.ZXY:
            self._x = s1 * c2 * c3 - c1 * s2 * s3
            self._y = c1 * s2 * c3 + s1 * c2 * s3
            self._z = c1 * c2 * s3 + s1 * s2 * c3
            self._w = c1 * c2 * c3 - s1 * s2 * s3
        elif order == Euler.RotationOrders.ZYX:
            self._x = s1 * c2 * c3 - c1 * s2 * s3
            self._y = c1 * s2 * c3 + s1 * c2 * s3
            self._z = c1 * c2 * s3 - s1 * s2 * c3
            self._w = c1 * c2 * c3 + s1 * s2 * s3
        elif order == Euler.RotationOrders.YZX:
            self._x = s1 * c2 * c3 + c1 * s2 * s3
            self._y = c1 * s2 * c3 + s1 * c2 * s3
            self._z = c1 * c2 * s3 - s1 * s2 * c3
            self._w = c1 * c2 * c3 - s1 * s2 * s3
        elif order == Euler.RotationOrders.XZY:
            self._x = s1 * c2 * c3 - c1 * s2 * s3
            self._y = c1 * s2 * c3 - s1 * c2 * s3
            self._z = c1 * c2 * s3 + s1 * s2 * c3
            self._w = c1 * c2 * c3 + s1 * s2 * s3

        if update:
            self._onChangeCallback()

        return self

    def setFromAxisAngle(self, axis: "three.Vector3", angle: float) -> "Quaternion":
        # assumes axis is normalized
        half_angle = angle / 2
        s = sin(half_angle)

        self._x = axis.x * s
        self._y = axis.y * s
        self._z = axis.z * s
        self._w = cos(half_angle)

        self._onChangeCallback()
        return self

    def setFromRotationMatrix(self, m: "three.Matrix4") -> "Quaternion":
        # assumes the upper 3x3 of m is a pure rotation matrix (i.e, unscaled)
        te = m.elements
        m11 = te[0]; m12 = te[4]; m13 = te[8]
        m21 = te[1]; m22 = te[5]; m23 = te[9]
        m31 = te[2]; m32 = te[6]; m33 = te[10]
        trace = m11 + m22 + m33

        if trace > 0:
            s = 0.5 / ((trace + 1.0) ** 0.5)
            self._w = 0.25 / s
            self._x = (m32 - m23) * s
            self._y = (m13 - m31) * s
            self._z = (m21 - m12) * s

        elif m11 > m22 and m11 > m33:
            s = 2.0 * ((1.0 + m11 - m22 - m33) ** 0.5)
            self._w = (m32 - m23) / s
            self._x = 0.25 * s
            self._y = (m12 + m21) / s
            self._z = (m13 + m31) / s

        elif m22 > m33:
            s = 2.0 * ((1.0 + m22 - m11 - m33) ** 0.5)
            self._w = (m13 - m31) / s
            self._x = (m12 + m21) / s
            self._y = 0.25 * s
            self._z = (m23 + m32) / s

        else:
            s = 2.0 * ((1.0 + m33 - m11 - m22) ** 0.5)
            self._w = (m21 - m12) / s
            self._x = (m13 + m31) / s
            self._y = (m23 + m32) / s
            self._z = 0.25 * s

        self._onChangeCallback()
        return self

    def setFromUnitVectors(self, v_from: "three.Vector3", v_to: "three.Vector3") -> "Quaternion":
        # assumes direction vectors v_from and v_to are normalized
        # eps = 0.000001
        eps = MACHINE_EPSILON
        r = v_from.dot(v_to) + 1

        if r < eps:
            r = 0
            if abs(v_from.x) > abs(v_from.z):
                self._x = -v_from.y
                self._y = v_from.x
                self._z = 0
                self._w = r
            else:
                self._x = 0
                self._y = -v_from.z
                self._z = v_from.y
                self._w = r
        else:
            self._x = v_from.y * v_to.z - v_from.z * v_to.y
            self._y = v_from.z * v_to.x - v_from.x * v_to.z
            self._z = v_from.x * v_to.y - v_from.y * v_to.x
            self._w = r

        return self.normalize()

    def angleTo(self, q: "Quaternion") -> float:
        return 2 * acos(abs(clamp(self.dot(q), -1, 1)))

    def rotateTowards(self, q: "Quaternion", step: float) -> "Quaternion":
        angle = self.angleTo(q)
        if angle == 0:
            return self
        t = min(1, step / angle)
        self.slerp(q, t)
        return self

    def identity(self):
        return self.set( 0, 0, 0, 1 )

    def inverse(self) -> "Quaternion":
        # quaternion is assumed to have unit length
        return self.conjugate()

    def invert(self) -> "Quaternion":
        # quaternion is assumed to have unit length
        return self.conjugate()

    def conjugate(self) -> "Quaternion":
        self._x *= -1
        self._y *= -1
        self._z *= -1

        self._onChangeCallback()
        return self

    def dot(self, q: "Quaternion") -> float:
        return self._x * q.x + self._y * q.y + self._z * q.z + self._w * q.w

    def length_sq(self) -> float:
        return self._x * self._x + self._y * self._y + self._z * self._z + self._w * self._w

    def length(self) -> float:
        return self.length_sq() ** 0.5

    def normalize(self) -> "Quaternion":
        length = self.length()

        if length == 0:
            self._x = 0
            self._y = 0
            self._z = 0
            self._w = 1
        else:
            self._x /= length
            self._y /= length
            self._z /= length
            self._w /= length

        self._onChangeCallback()
        return self

    def multiply(self, q: "Quaternion") -> "Quaternion":
        return self.multiplyQuaternions(self, q)

    def premultiply(self, q: "Quaternion") -> "Quaternion":
        return self.multiplyQuaternions(q, self)

    def multiplyQuaternions(self, a: "Quaternion", b: "Quaternion") -> "Quaternion":
        qax = a._x
        qay = a._y
        qaz = a._z
        qaw = a._w
        qbx = b._x
        qby = b._y
        qbz = b._z
        qbw = b._w

        self.x = qax * qbw + qaw * qbx + qay * qbz - qaz * qby
        self.y = qay * qbw + qaw * qby + qaz * qbx - qax * qbz
        self.z = qaz * qbw + qaw * qbz + qax * qby - qay * qbx
        self.w = qaw * qbw - qax * qbx - qay * qby - qaz * qbz

        self._onChangeCallback()

        return self

    def slerp(self, qb: "Quaternion", t: float) -> "Quaternion":
        if t == 0:
            return self
        elif t == 1:
            return self.copy(qb)

        x = self._x
        y = self._y
        z = self._z
        w = self._w
        cos_half_theta = w * qb.w + x * qb.x + y * qb.y + z * qb.z
        if cos_half_theta < 0:
            self._w = -qb.w
            self._x = -qb.x
            self._y = -qb.y
            self._z = -qb.z
            cos_half_theta = -cos_half_theta
        else:
            self.copy(qb)

        if cos_half_theta >= 1.0:
            self._w = w
            self._x = x
            self._y = y
            self._z = z
            return self

        sqr_sin_half_theta = 1.0 - cos_half_theta * cos_half_theta
        if sqr_sin_half_theta <= MACHINE_EPSILON:
            s = 1 - t
            self._w = s * w + t * self._w
            self._x = s * x + t * self._x
            self._y = s * y + t * self._y
            self._z = s * z + t * self._z
            self.normalize()
            self._onChangeCallback()
            return self

        sin_half_theta = sqr_sin_half_theta ** 0.5
        half_theta = atan2(sin_half_theta, cos_half_theta)
        ratio_a = sin((1 - t) * half_theta) / sin_half_theta
        ratio_b = sin(t * half_theta) / sin_half_theta

        self._w = w * ratio_a + self._w * ratio_b
        self._x = x * ratio_a + self._x * ratio_b
        self._y = y * ratio_a + self._y * ratio_b
        self._z = z * ratio_a + self._z * ratio_b

        self._onChangeCallback()
        return self

    def slerpQuaternions( self, qa, qb, t ):
        return self.copy( qa ).slerp( qb, t )

    def random(self):
        import random
        u1 = random.random()
        sqrt1u1 = ( 1 - u1 ) ** 0.5
        sqrtu1 = u1 ** 0.5

        u2 = 2 * pi * random.random()

        u3 = 2 * pi * random.random()

        return self.set(
            sqrt1u1 * cos( u2 ),
            sqrtu1 * sin( u3 ),
            sqrtu1 * cos( u3 ),
            sqrt1u1 * sin( u2 ),
        ); 

    def equals(self, quaternion: "Quaternion") -> bool:
        return (
            quaternion._x == self._x
            and quaternion._y == self._y
            and quaternion._z == self._z
            and quaternion._w == self._w
        )

    def __eq__(self, other: "Quaternion") -> bool:
        return isinstance(other, Quaternion) and self.equals(other)

    def fromArray(self, array: list, offset: int = 0) -> "Quaternion":
        self._x = array[offset]
        self._y = array[offset + 1]
        self._z = array[offset + 2]
        self._w = array[offset + 3]
        self._onChangeCallback()
        return self

    def toArray(self, array: list = None, offset: int = 0) -> list:
        if array is None:
            array = []

        padding = offset + 4 - len(array)
        if padding > 0:
            array.extend((None for _ in range(padding)))

        array[offset] = self._x
        array[offset + 1] = self._y
        array[offset + 2] = self._z
        array[offset + 3] = self._w
        return array

    def fromBufferAttribute( self, attribute:' three.BufferAttribute', index ):
        self._x = attribute.getX( index )
        self._y = attribute.getY( index )
        self._z = attribute.getZ( index )
        self._w = attribute.getW( index )
        return self


    def _onChange( self, callback ):
        self._onChangeCallback = callback
        return self
        
    def _onChangeCallback(self):
        pass

    
    @property
    def isQuaternion(self):
        return True
