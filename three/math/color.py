import math
import three
from ..structure import NoneAttribute, Dict
from .math_utils import clamp, euclideanModulo, lerp
from .color_management import ColorManagement, LinearToSRGB, SRGBToLinear
from ..constants import SRGBColorSpace, LinearSRGBColorSpace


_rgb = Dict({ 'r': 0, 'g': 0, 'b': 0 })
_hslA = Dict({ 'h': 0, 's': 0, 'l': 0 })
_hslB = Dict({ 'h': 0, 's': 0, 'l': 0 })


def hue2rgb( p, q, t ):
    if ( t < 0 ):
        t += 1
    if ( t > 1 ):
        t -= 1
    if ( t < 1 / 6 ):
        return p + ( q - p ) * 6 * t
    if ( t < 1 / 2 ):
        return q
    if ( t < 2 / 3 ):
        return p + ( q - p ) * 6 * ( 2 / 3 - t )
    return p

def toComponents( source, target ):
    target.r = source.r
    target.g = source.g
    target.b = source.b
    return target

# @TODO ColorSpace
class Color(NoneAttribute):

    isColor = True

    def __init__(self, r=None, g=None, b=None) -> None:
        
        if g is None and b is None:
            self.set(r)
        else:
            self.setRGB(r, g, b)

    
    def __repr__(self) -> str:
        return f"Color({self.r}, {self.g}, {self.b})"

    def set(self, value):
        if value is None:
            value = 0
            
        if value and isinstance(value, Color):
            self.copy(value)

        elif type(value) == int:
            self.setHex(value)

        elif type(value) == str:
            self.setStyle(value)

        return self


    def setScalar(self, scalar):
        self.r = scalar
        self.g = scalar
        self.b = scalar
        return self

    def setHex(self, hex, colorSpace = SRGBColorSpace):
        hex = math.floor(hex)

        self.r = (hex >> 16 & 255) / 255
        self.g = (hex >> 8 & 255) / 255
        self.b = (hex & 255) / 255
        
        ColorManagement.toWorkingColorSpace( self, colorSpace )
        return self

    def setRGB(self, r, g, b, colorSpace = LinearSRGBColorSpace):
        self.r = r
        self.g = g
        self.b = b

        ColorManagement.toWorkingColorSpace( self, colorSpace )
        return self

    def setHSL(self, h, s, l, colorSpace = LinearSRGBColorSpace):
        h = euclideanModulo( h, 1 )
        s = clamp( s, 0, 1 )
        l = clamp( l, 0, 1 )

        if ( s == 0 ):

            self.r = self.g = self.b = l

        else:

            p = l * ( 1 + s ) if l <= 0.5  else l + s - ( l * s )
            q = ( 2 * l ) - p

            self.r = hue2rgb( q, p, h + 1 / 3 )
            self.g = hue2rgb( q, p, h )
            self.b = hue2rgb( q, p, h - 1 / 3 )

        ColorManagement.toWorkingColorSpace( self, colorSpace )

        return self

    def setStyle(self, style, colorSpace = SRGBColorSpace):
        raise NotImplementedError()

    def setColorName(self, name):
        raise NotImplementedError()

    def copy(self, color:'Color') -> 'Color':
        self.r = color.r
        self.g =color.g
        self.b = color.b
        return self

    def clone(self) -> 'Color':
        return Color().copy(self)

    def copySRGBToLinear( self, color ):
        self.r = LinearToSRGB( color.r )
        self.g = LinearToSRGB( color.g )
        self.b = LinearToSRGB( color.b )
        return self

    def copyLinearToSRGB( self, color ):
        self.r = LinearToSRGB( color.r )
        self.g = LinearToSRGB( color.g )
        self.b = LinearToSRGB( color.b )
        return self

    def convertSRGBToLinear(self):
        self.copySRGBToLinear( self )
        return self

    def convertLinearToSRGB(self):
        self.copyLinearToSRGB( self )
        return self


    def getHex(self,colorSpace = SRGBColorSpace):
        ColorManagement.fromWorkingColorSpace( toComponents( self, _rgb ), colorSpace )
        return int( self.r * 255 ) << 16 ^ int( self.g * 255 ) << 8 ^ int( self.b * 255 ) << 0

    def getHexString(self, colorSpace = SRGBColorSpace):
        return ( '000000' + hex(self.getHex(colorSpace)) )[-6:]

    def getHSL(self,  target, colorSpace = LinearSRGBColorSpace ):
        ColorManagement.fromWorkingColorSpace( toComponents( self, _rgb ), colorSpace )
        r = _rgb.r
        g = _rgb.g
        b = _rgb.b
        _max = max( r, g, b )
        _min = min( r, g, b )

        lightness = ( _min + _max ) / 2.0

        if _min == _max :
            hue = 0
            saturation = 0
        else:
            delta = _max - _min
            saturation = delta / ( _max + _min ) if lightness <= 0.5 else  delta / ( 2 - _max - _min )

            if _max == r:
                hue = ( g - b ) / delta + ( 6 if g < b else 0 )
            elif _max == g:
                hue = ( b - r ) / delta + 2
            elif _max == b:
                hue = ( r - g ) / delta + 4

            hue /= 6

        target.h = hue
        target.s = saturation
        target.l = lightness

        return target

    def getRGB( self, target,  colorSpace = LinearSRGBColorSpace):
        ColorManagement.fromWorkingColorSpace( toComponents( self, _rgb ), colorSpace )
        target.r = _rgb.r
        target.g = _rgb.g
        target.b = _rgb.b
        return target

    def getStyle( self, colorSpace = SRGBColorSpace ):
        ColorManagement.fromWorkingColorSpace( toComponents( self, _rgb ), colorSpace )

        if ( colorSpace != SRGBColorSpace ):
            # Requires CSS Color Module Level 4 (https://www.w3.org/TR/css-color-4/).
            return f'color({ colorSpace } { _rgb.r } { _rgb.g } { _rgb.b })'

        return f'rgb({( _rgb.r * 255 ) | 0},{( _rgb.g * 255 ) | 0},{( _rgb.b * 255 ) | 0})'

    def offsetHSL( self, h, s, l ):
        self.getHSL( _hslA )
        _hslA.h += h; _hslA.s += s; _hslA.l += l
        self.setHSL( _hslA.h, _hslA.s, _hslA.l )
        return self

    def add( self, color ):
        self.r += color.r
        self.g += color.g
        self.b += color.b
        return self


    def addColors( self, color1, color2 ):
        self.r = color1.r + color2.r
        self.g = color1.g + color2.g
        self.b = color1.b + color2.b
        return self


    def addScalar( self, s ):
        self.r += s
        self.g += s
        self.b += s
        return self

    def sub( self, color ):
        self.r = max( 0, self.r - color.r )
        self.g = max( 0, self.g - color.g )
        self.b = max( 0, self.b - color.b )
        return self

    def multiply( self, color ):
        self.r *= color.r
        self.g *= color.g
        self.b *= color.b
        return self

    def multiplyScalar( self, s ):
        self.r *= s
        self.g *= s
        self.b *= s
        return self

    def lerp( self, color, alpha ):
        self.r += ( color.r - self.r ) * alpha
        self.g += ( color.g - self.g ) * alpha
        self.b += ( color.b - self.b ) * alpha
        return self

    def lerpColors( self, color1, color2, alpha ):

        self.r = color1.r + ( color2.r - color1.r ) * alpha
        self.g = color1.g + ( color2.g - color1.g ) * alpha
        self.b = color1.b + ( color2.b - color1.b ) * alpha

        return self


    def lerpHSL(self, color:'Color', alpha ):
        self.getHSL( _hslA )
        color.getHSL( _hslB )
        h = self.lerp( _hslA.h, _hslB.h, alpha )
        s = self.lerp( _hslA.s, _hslB.s, alpha )
        l = self.lerp( _hslA.l, _hslB.l, alpha )
        self.setHSL( h, s, l )
        return self

    def equals( self, c:'Color' ):
        return ( c.r == self.r ) and ( c.g == self.g ) and ( c.b == self.b )

    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, Color) and  self.equals(__o)

    def __hash__(self) -> int:
        return hash( ( self.r, self.g, self.b ) )

    def fromArray(self, array, offset = 0 ):
        self.r = array[ offset ]
        self.g = array[ offset + 1 ]
        self.b = array[ offset + 2 ]
        return self

    def toArray( self, array = [], offset = 0 ):
        array[ offset ] = self.r
        array[ offset + 1 ] = self.g
        array[ offset + 2 ] = self.b

        return array

    def fromBufferAttribute( self, attribute:'three.BufferAttribute', index ):

        self.r = attribute.getX( index )
        self.g = attribute.getY( index )
        self.b = attribute.getZ( index )

        if attribute.normalized:
            # assuming Uint8Array
            self.r /= 255
            self.g /= 255
            self.b /= 255

        return self
