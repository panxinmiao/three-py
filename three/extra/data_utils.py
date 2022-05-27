import warnings
from ..math.math_utils import clamp
from ..structure import Float32Array, Uint32Array

class DataUtils:

    @staticmethod
    def toHalfFloat(val):
        if abs(val) > 65504:
            warnings.warn('THREE.DataUtils.toHalfFloat(): Value out of range.')

        val = clamp( val, - 65504, 65504 )

        _floatView[ 0 ] = val
        f = _uint32View[ 0 ]
        e = ( f >> 23 ) & 0x1ff
        return _baseTable[ e ] + ( ( f & 0x007fffff ) >> _shiftTable[ e ] )


    @staticmethod
    def fromHalfFloat(val):
        m = val >> 10
        _uint32View[0] = _mantissaTable[_offsetTable[m] + (val & 0x3ff)] + _exponentTable[m]
        return _floatView[0]


# float32 to float16 helpers

_buffer = bytearray(4)
_floatView = Float32Array.wrap(_buffer)
_uint32View = Uint32Array.wrap(_buffer)

_baseTable =  Uint32Array( 512 )
_shiftTable = Uint32Array( 512 )


for i in range(256):
    e = i - 127
    # very small number(0, -0)
    if e < - 27:
        _baseTable[i] = 0x0000
        _baseTable[i | 0x100] = 0x8000
        _shiftTable[i] = 24
        _shiftTable[i | 0x100] = 24

        # small number(denorm)
    elif e < - 14:
        _baseTable[i] = 0x0400 >> (- e - 14)
        _baseTable[i | 0x100] = (0x0400 >> (- e - 14)) | 0x8000
        _shiftTable[i] = - e - 1
        _shiftTable[i | 0x100] = - e - 1

        # normal number
    elif e <= 15:
        _baseTable[i] = (e + 15) << 10
        _baseTable[i | 0x100] = ((e + 15) << 10) | 0x8000
        _shiftTable[i] = 13
        _shiftTable[i | 0x100] = 13

        # large number(Infinity, -Infinity)
    elif e < 128:
        _baseTable[i] = 0x7c00
        _baseTable[i | 0x100] = 0xfc00
        _shiftTable[i] = 24
        _shiftTable[i | 0x100] = 24

        # stay(NaN, Infinity, -Infinity)
    else:
        _baseTable[i] = 0x7c00
        _baseTable[i | 0x100] = 0xfc00
        _shiftTable[i] = 13
        _shiftTable[i | 0x100] = 13


# float16 to float32 helpers

_mantissaTable =  Uint32Array( 2048 )
_exponentTable =  Uint32Array( 64 )
_offsetTable =  Uint32Array( 64 )

for i in range(1, 1024):
    m = i << 13
    # zero pad mantissa bits
    e = 0
    # zero exponent

    # normalized
    while (m & 0x00800000) == 0:

        m <<= 1
        e -= 0x00800000
        # decrement exponent

    m &= ~ 0x00800000
    # clear leading 1 bit
    e += 0x38800000
    # adjust bias

    _mantissaTable[i] = m | e


for i in range(1024, 2048):
    _mantissaTable[ i ] = 0x38000000 + ( ( i - 1024 ) << 13 )


for i in range(1, 31):
    _exponentTable[ i ] = i << 23

_exponentTable[ 31 ] = 0x47800000
_exponentTable[ 32 ] = 0x80000000

for i in range(33, 63):
    _exponentTable[ i ] = 0x80000000 + ( ( i - 32 ) << 23 )

_exponentTable[ 63 ] = 0xc7800000

for i in range(1, 64):
	if i != 32:
		_offsetTable[ i ] = 1024
