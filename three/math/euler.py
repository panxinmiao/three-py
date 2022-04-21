from enum import Enum
from math import asin, atan2

from .math_utils import clamp
from .matrix4 import Matrix4
from .quaternion import Quaternion
from ..structure import NoneAttribute

import three

class Euler(NoneAttribute):
    class RotationOrders(Enum):
        XYZ = "XYZ"
        YZX = "YZX"
        ZXY = "ZXY"
        XZY = "XZY"
        YXZ = "YXZ"
        ZYX = "ZYX"

    DefaultOrder = RotationOrders.XYZ

    def __init__(
        self, x: float = 0, y: float = 0, z: float = 0, order: RotationOrders = None
    ) -> None:
        self._x = x
        self._y = y
        self._z = z
        self._order = order if order is not None else self.DefaultOrder

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
    def order(self):
        return self._order

    @order.setter
    def order(self, value: RotationOrders):
        self._order = value
        self._onChangeCallback()

    def __repr__(self) -> str:
        return f"Euler({self._x}, {self._y}, {self._z}, {self._order})"

    def set( self, x: float, y: float, z: float, order: RotationOrders = None ) -> "Euler":
        self._x = x
        self._y = y
        self._z = z
        self._order = order or self._order
        
        self._onChangeCallback()
        return self

    def clone(self) -> "Euler":
        return Euler(self._x, self._y, self._z, self._order)

    def copy(self, euler: "Euler") -> "Euler":
        self._x = euler._x
        self._y = euler._y
        self._z = euler._z
        self._order = euler._order

        self._onChangeCallback()
        return self

    def setFromRotationMatrix(
        self, m: "Matrix4", order: RotationOrders = None, update = True
    ) -> "Euler":
        # assumes the upper 3x3 of m is a pure rotation matrix (i.e, unscaled)
        te = m.elements
        m11 = te[0]
        m12 = te[4]
        m13 = te[8]
        m21 = te[1]
        m22 = te[5]
        m23 = te[9]
        m31 = te[2]
        m32 = te[6]
        m33 = te[10]

        order = order or self._order

        if order == Euler.RotationOrders.XYZ:
            self._y = asin(clamp(m13, -1, 1))
            if abs(m13) < 0.9999999:
                self._x = atan2(-m23, m33)
                self._z = atan2(-m12, m11)
            else:
                self._x = atan2(m32, m22)
                self._z = 0

        elif order == Euler.RotationOrders.YXZ:
            self._x = asin(-clamp(m23, -1, 1))
            if abs(m23) < 0.9999999:
                self._y = atan2(m13, m33)
                self._z = atan2(m21, m22)
            else:
                self._y = atan2(-m31, m11)
                self._z = 0

        elif order == Euler.RotationOrders.ZXY:
            self._x = asin(clamp(m32, -1, 1))
            if abs(m32) < 0.9999999:
                self._y = atan2(-m31, m33)
                self._z = atan2(-m12, m22)
            else:
                self._y = 0
                self._z = atan2(m21, m11)

        elif order == Euler.RotationOrders.ZYX:
            self._y = asin(-clamp(m31, -1, 1))
            if abs(m31) < 0.9999999:
                self._x = atan2(m32, m33)
                self._z = atan2(m21, m11)
            else:
                self._x = 0
                self._z = atan2(-m12, m22)

        elif order == Euler.RotationOrders.YZX:
            self._z = asin(clamp(m21, -1, 1))
            if abs(m21) < 0.9999999:
                self._x = atan2(-m23, m22)
                self._y = atan2(-m31, m11)
            else:
                self._x = 0
                self._y = atan2(m13, m33)

        elif order == Euler.RotationOrders.XZY:
            self._z = asin(-clamp(m12, -1, 1))
            if abs(m12) < 0.9999999:
                self._x = atan2(m32, m22)
                self._y = atan2(m13, m11)
            else:
                self._x = atan2(-m23, m33)
                self._y = 0

        else:
            raise ValueError(f"{order} not supported")

        self._order = order

        if update:
            self._onChangeCallback()

        return self

    def setFromQuaternion(
        self, q: "Quaternion", order: RotationOrders = None, update = True
    ) -> "Euler":
        _tmp_matrix4.makeRotationFromQuaternion(q)
        return self.setFromRotationMatrix(_tmp_matrix4, order=order, update = update)

    def setFromVector3(self, v: "three.Vector3", order: RotationOrders = None) -> "Euler":
        return self.set(v.x, v.y, v.z, order=order)

    def reorder(self, new_order: RotationOrders) -> "Euler":
        # warning: revolution info lost
        _tmp_quaternion.setFromEuler(self)
        return self.setFromQuaternion(_tmp_quaternion, order=new_order)

    def equals(self, euler: "Euler") -> bool:
        return (
            euler._x == self._x
            and euler._y == self._y
            and euler._z == self._z
            and euler._order == self._order
        )

    def __eq__(self, other: "Euler") -> bool:
        return isinstance(other, Euler) and self.equals(other)

    def fromArray(self, array: list) -> "Euler":
        self._x = array[0]
        self._y = array[1]
        self._z = array[2]
        if len(array) >= 4:
            self._order = array[3]

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
        array[offset + 3] = self._order
        return array

    # @TODO remove
    def toVector3(self, output: "three.Vector3" = None) -> "three.Vector3":
        #from .vector3 import Vector3

        if output is not None:
            return output.set(self._x, self._y, self._z)
        else:
            return three.Vector3(self._x, self._y, self._z)

    def _onChange( self, callback ):
        self._onChangeCallback = callback
        return self
        
    def _onChangeCallback(self):
        pass


_tmp_matrix4 = Matrix4()
_tmp_quaternion = Quaternion()

# from .vector3 import Vector3
#Vector3_cls = "Vector3"