import abc
import uuid
import numpy as np
from typing import Iterable

class TypedArray(metaclass=abc.ABCMeta):
    
    @classmethod
    def wrap(cls, buffer: memoryview, byteOffset = 0, length = -1) -> 'TypedArray':
        ary = cls()
        ary._ndarray = np.frombuffer(buffer, dtype=cls._dtype, count = length, offset = byteOffset)
        return ary

    @classmethod
    def allocate(cls, length):
        ary = cls()
        ary._ndarray = np.zeros(length, dtype=cls._dtype)
        return ary

    def __init__(self, __initializer: list = []) -> None:
        self._uuid = uuid.uuid1()
        if type(__initializer) == int:
            self._ndarray = np.zeros(__initializer, dtype=self._dtype)
        elif isinstance(__initializer, TypedArray):
            self._ndarray =np.array(__initializer._ndarray, dtype=self._dtype)
        elif isinstance(__initializer, Iterable):
            self._ndarray = np.array(__initializer, dtype=self._dtype)

    @property
    @abc.abstractmethod
    def bytes_per_element(self) -> int:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def _dtype(self) -> str:
        raise NotImplementedError

    @property
    def uuid(self):
        return self._uuid

    @property
    def buffer(self):
        return self._ndarray.data

    @property
    def byteLength(self):
        return self.length * self.bytes_per_element

    @property
    def length(self):
        return self._ndarray.size

    def copy(self):
        return self.__copy__()

    def copy_buffer(self, buffer: 'memoryview'):
        self._ndarray = np.frombuffer(buffer, dtype=self._dtype)
        return self

    def __copy__(self):
        return self.__class__.wrap(self.buffer)
    
    def range_buffer(self):
        return self._ndarray.data

    def __len__(self):
        return self.length

    def __getitem__(self, n):
        if isinstance(n, int):
            return self._ndarray[n]
    
    def __setitem__(self, n , v):
        self._ndarray[n] = v

    def __repr__(self) -> str:
        return f'<{self.name}> {self._ndarray}'

    def __iter__(self):
        return self._ndarray.__iter__()

    def set(self, v, offset=0):
        self[offset: offset+len(v)] = v

    def at(self, position):
        return self[position]

    def append(self, *value):
        self._ndarray = np.append(self._ndarray, value)

    def extend(self, values):
        self._ndarray = np.append(self._ndarray, values)


class Int8Array(TypedArray):
    name = 'Int8Array'
    _dtype = np.int8


class Uint8Array(TypedArray):
    name = 'Uint8Array'
    _dtype = np.uint8
    bytes_per_element = 1


class Int16Array(TypedArray):
    name = 'Int16Array'
    _dtype = np.int16
    bytes_per_element = 2


class Uint16Array(TypedArray):
    name = 'Uint16Array'
    _dtype = np.uint16
    bytes_per_element = 2


class Int32Array(TypedArray):
    name = 'Int32Array'
    _dtype = np.int32
    bytes_per_element = 4


class Uint32Array(TypedArray):
    name = 'Uint32Array'
    _dtype = np.uint32
    bytes_per_element = 4


class Float16Array(TypedArray):
    name = 'Float16Array'
    _dtype = np.float16
    bytes_per_element = 2


class Float32Array(TypedArray):
    name = 'Float32Array'
    _dtype = np.float32
    bytes_per_element = 4


class Float64Array(TypedArray):
    name = 'Float64Array'
    _dtype = np.float64
    bytes_per_element = 8


class BigInt64Array(TypedArray):
    name = 'BigInt64Array'
    _dtype = np.int64
    bytes_per_element = 8


class BigUint64Array(TypedArray):
    name = 'BigUint64Array'
    _dtype = np.uint64
    bytes_per_element = 8
