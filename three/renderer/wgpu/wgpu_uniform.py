from array import array
from ...structure import NoneAttribute
from ...math import Vector2, Vector3, Vector4, Color, Matrix3, Matrix4

class WgpuUniform(NoneAttribute):

    def __init__(self, name, value = None) -> None:
        
        self.name = name
        self.value = value

        self.boundary = 0
        self.itemSize = 0

        self._offset = 0

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, v):
        self._offset = int(v)

    def setValue( self, value ):
        self.value = value

    def getValue(self):
        return self.value

    def getBuffer(self) -> memoryview:
        raise NotImplementedError()


class FloatUniform(WgpuUniform):
    isFloatUniform = True

    def __init__(self, name, value=0) -> None:
        super().__init__(name, value)

        self.boundary = 4
        self.itemSize = 1
    
    def getBuffer(self):
        v = self.getValue() if self.getValue() is not None else 0
        # return memoryview((ctypes.c_float*1)(v))
        return memoryview(array('f', [v]))

class Vector2Uniform(WgpuUniform):
    isVector2Uniform = True

    def __init__(self, name, value=None) -> None:
        super().__init__(name, value or Vector2())

        self.boundary = 8
        self.itemSize = 2

    def getBuffer(self):
        return memoryview(self.getValue()._buffer)

class Vector3Uniform(WgpuUniform):
    isVector3Uniform = True

    def __init__(self, name, value=None) -> None:
        super().__init__(name, value or Vector3())

        self.boundary = 16
        self.itemSize = 3

    def getBuffer(self):
        return memoryview(self.getValue()._buffer)


class Vector4Uniform(WgpuUniform):
    isVector4Uniform = True

    def __init__(self, name, value=None) -> None:
        super().__init__(name, value or Vector4())

        self.boundary = 16
        self.itemSize = 4

    def getBuffer(self):
        return memoryview(self.getValue()._buffer)


class ColorUniform(WgpuUniform):
    isColorUniform = True

    def __init__(self, name, value=None) -> None:
        super().__init__(name, value or Color())

        self.boundary = 16
        self.itemSize = 3

    def getBuffer(self):
        return memoryview(self.getValue()._buffer)

class Matrix3Uniform(WgpuUniform):
    isMatrix3Uniform = True

    def __init__(self, name, value=None) -> None:
        super().__init__(name, value or Matrix3())

        self.boundary = 48
        self.itemSize = 12

    def getBuffer(self):
        buffer = array('f', [0]*12)
        a = self.getValue().elements

        buffer[0:3] = a[0:3]
        buffer[4:7] = a[3:6]
        buffer[8:11] = a[6:9]

        return memoryview(buffer)


class Matrix4Uniform(WgpuUniform):
    isMatrix4Uniform = True

    def __init__(self, name, value=None) -> None:
        super().__init__(name, value or Matrix4())

        self.boundary = 64
        self.itemSize = 16
    
    def getBuffer(self):
        return memoryview(self.getValue()._buffer)


