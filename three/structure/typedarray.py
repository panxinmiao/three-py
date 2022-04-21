# from ..bytebuffer import ByteBuffer
import abc
import struct, uuid

class TypedArray(metaclass=abc.ABCMeta):

    @classmethod
    def wrap(cls, buffer: bytearray, byteOffset = 0, length = None) -> 'TypedArray':
        ary = cls()
        array_len = len(buffer)
        if not (0 <= byteOffset <= array_len):
            raise ValueError('Offset out of range')
        el = ary.bytes_per_element

        if byteOffset % el !=0:
            raise ValueError(f'start offset of {ary.name} should be a multiple of {el}')

        if length is None:
            byteLength = array_len - byteOffset
            if byteLength % el !=0:
                raise ValueError(f'byte length of {ary.name} should be a multiple of {el}')
            length = int(byteLength / el)
        else:
            byteLength = length * el
            if not (0 <= byteLength <= array_len - byteOffset):
                raise ValueError('Length out of range')

        ary._buffer = buffer
        ary._byteOffset = byteOffset
        #ary._byteLength = byteLength
        ary._length = length
        return ary

    @classmethod
    def allocate(cls, length):
        ary = cls()
        ary._length = length
        ary._buffer = bytearray(length * ary.bytes_per_element)
        ary._byteOffset = 0
        return ary

    @classmethod
    def fromTypeArray(cls, array: 'TypedArray'):
        ary = cls()

        ary._buffer = array.buffer
        ary._byteOffset = array.byteOffset
        byteLength = array.byteLength
        
        el = ary.bytes_per_element
        if byteLength % el !=0:
            raise ValueError(f'byte length of {ary.name} should be a multiple of {el}')
        ary._length = int(byteLength / el)
        return ary
        

    # def __init__(self, buffer: bytearray, byteOffset = 0, length = None) -> None:
    #     pass

    def __init__(self, __initializer: list = []) -> None:
        self._uuid = uuid.uuid1()
        self._length = len(__initializer)
        bytes = struct.pack(f'{self._length}{self.struct_symbol}', *__initializer)
        self._buffer = bytearray(bytes)
        self._byteOffset = 0
        #self._byteLength = len(bytes)

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
    def struct_symbol(self) -> str:
        raise NotImplementedError

    @property
    def uuid(self):
        return self._uuid

    @property
    def buffer(self):
        return self._buffer

    @property
    def byteOffset(self):
        return self._byteOffset

    @property
    def byteLength(self):
        return self.length * self.bytes_per_element

    @property
    def length(self):
        max_length = int((len(self._buffer) - self._byteOffset) / self.bytes_per_element)
        return self._length if self._length< max_length else max_length

    def copy(self):
        return self.__copy__()

    def copy_buffer(self, buffer: 'bytearray'):
        self._buffer[:] = buffer
        self._byteOffset = 0
        self._length = int(len(self._buffer) / self.bytes_per_element)
        return self

    def __copy__(self):
        # return self.__class__.wrap(self.buffer.copy(), byteOffset=self.byteOffset, length=self.length)
        return self.__class__.wrap(self.range_buffer())

    def range_buffer(self):
        return self._buffer[self.byteOffset: self.byteLength + self.byteOffset]

    def __getitem__(self, n):
        if isinstance(n, int):
            src_offset = self._byteOffset + n * self.bytes_per_element
            return struct.unpack_from(self.struct_symbol, self._buffer, src_offset)[0]
        if isinstance(n, slice):
            # start = n.start or 0
            # stop = n.stop or self.length
            # start = start*self.bytes_per_element
            # stop = self.byteOffset + stop*self.bytes_per_element


            _start = n.start*self.bytes_per_element if n.start else None
            _stop = n.stop*self.bytes_per_element if n.stop else None
            #_step = n.step*self.bytes_per_element if n.step else None

            _s = slice(_start, _stop , None)
            buffer = self.buffer[_s]
            return self.__class__.wrap(buffer, 0)
            #return self.__class__(buffer, 0)

    
    def __setitem__(self, n , v):
        if isinstance(n, int):
            if n >= self.length:
                raise ValueError(f"index out of range ({self.length})")
            if not isinstance(v, (int, float)):
                raise ValueError(f"a number is required (got type {v.__class__.__name__})")
            src_offset = self._byteOffset + n * self.bytes_per_element
            struct.pack_into(self.struct_symbol, self._buffer, src_offset, v)
            #struct.unpack_from(self.struct_symbol, self._buffer, src_offset)[0]
        if isinstance(n, slice):
            if isinstance(v, list):
                bytes = struct.pack(f'{len(v)}{self.struct_symbol}', *v)
            elif type(v) == self.__class__:
                bytes = v.range_buffer()
            elif isinstance(v, TypedArray):
                v = v.getValues()
                bytes = struct.pack(f'{len(v)}{self.struct_symbol}', *v)
            else:
                raise ValueError(f"bad argument type for built-in operation")

            _start = n.start*self.bytes_per_element if n.start else None
            _stop = n.stop*self.bytes_per_element if n.stop else None
            #_step = n.step*self.bytes_per_element if n.step else None

            _s = slice(_start, _stop , None)

            #self._length += (len(v) - len(self[n]))

            self.buffer[_s] = bytes

    
    def __len__(self):
        return self.length

    def __iter__(self):
        return self
    
    def __next__(self):
        if not hasattr(self, '_iter_index'):
            self._iter_index = 0

        if self._iter_index < self.length:
            ret = self[self._iter_index ]
            self._iter_index += 1
            return ret
        else:
            raise StopIteration

    def __repr__(self) -> str:
        s = f'<{self.name}> ['
        for i in range(self.length):
            s+= f'{self[i]}'
            if i == self.length-1: break
            s+=', '
            if i == 4:
                s += '... '
                break

        s += ']'
        return s


    def set(self, v, offset = 0):
        self[offset: offset+len(v)] = v


    def at(self, position):
        return self[position]

    def getValues(self, start=0, cnt=None):
        _start = start*self.bytes_per_element

        if cnt is None:
            cnt = self.length - start

        return struct.unpack_from(f'{cnt}{self.struct_symbol}', self._buffer, _start)


    def copyWithin(self, target, start, end):
        raise NotImplementedError

    def entries(self):
        raise NotImplementedError

    def every(self):
        raise NotImplementedError

    def fill(self, v, start, end):
        raise NotImplementedError

    def filter(self, func):
        raise NotImplementedError


class Int8Array(TypedArray):
    name = 'Int8Array'
    bytes_per_element = 1
    struct_symbol = 'b'

class Uint8Array(TypedArray):
    name = 'Uint8Array'
    bytes_per_element = 1
    struct_symbol = 'B'

class Int16Array(TypedArray):
    name = 'Int16Array'
    bytes_per_element = 2
    struct_symbol = 'h'

class Uint16Array(TypedArray):
    name = 'Uint16Array'
    bytes_per_element = 2
    struct_symbol = 'H'

class Int32Array(TypedArray):
    name = 'Int32Array'
    bytes_per_element = 4
    struct_symbol = 'i'

class Uint32Array(TypedArray):
    name = 'Uint32Array'
    bytes_per_element = 4
    struct_symbol = 'I'

# class Float16Array(TypedArray):
#     name = 'Float32Array'
#     bytes_per_element = 2
#     struct_symbol = 'f'

class Float32Array(TypedArray):
    name = 'Float32Array'
    bytes_per_element = 4
    struct_symbol = 'f'

class Float64Array(TypedArray):
    name = 'Float64Array'
    bytes_per_element = 8
    struct_symbol = 'd'

class BigInt64Array(TypedArray):
    name = 'BigInt64Array'
    bytes_per_element = 8
    struct_symbol = 'q'

class BigUint64Array(TypedArray):
    name = 'BigUint64Array'
    bytes_per_element = 8
    struct_symbol = 'Q'

