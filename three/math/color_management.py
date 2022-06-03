import math
from warnings import warn
from ..constants import SRGBColorSpace, LinearSRGBColorSpace

def SRGBToLinear( c ):
    return c * 0.0773993808 if c < 0.04045 else math.pow( c * 0.9478672986 + 0.0521327014, 2.4 )

def LinearToSRGB( c ):
    return c * 12.92 if c < 0.0031308 else 1.055 * ( math.pow( c, 0.41666 ) ) - 0.055

FN = {
    SRGBColorSpace: { LinearSRGBColorSpace : SRGBToLinear },
    LinearSRGBColorSpace: { SRGBColorSpace : LinearToSRGB },
}


class __ColorManagement:

    def __init__(self) -> None:
        self.legacyMode= True
        self._workingColorSpace= LinearSRGBColorSpace

    @property
    def workingColorSpace(self):
        return LinearSRGBColorSpace

    @workingColorSpace.setter
    def workingColorSpace( self, colorSpace ):
        warn( 'ColorManagement: .workingColorSpace is readonly.' )

    def convert(self, color, sourceColorSpace, targetColorSpace):
        if self.legacyMode or sourceColorSpace == targetColorSpace or not sourceColorSpace or not targetColorSpace:
            return color

        if FN[ sourceColorSpace ] and FN[ sourceColorSpace ][ targetColorSpace ]:
            fn = FN[ sourceColorSpace ][ targetColorSpace ]
            color.r = fn( color.r )
            color.g = fn( color.g )
            color.b = fn( color.b )
            return color

        raise ( 'Unsupported color space conversion.' )

    
    def fromWorkingColorSpace( self, color, targetColorSpace ):
        return self.convert( color, self.workingColorSpace, targetColorSpace )

    def toWorkingColorSpace(self, color, sourceColorSpace ):
        return self.convert( color, sourceColorSpace, self.workingColorSpace )



ColorManagement = __ColorManagement()