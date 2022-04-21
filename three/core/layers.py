from ..structure import NoneAttribute

class Layers(NoneAttribute):

    def __init__(self) -> None:
        self.mask  = 1 | 0

    def set( self, channel ):
        self.mask = ( 1 << channel | 0 ) >> 0


    def enable( self, channel ):
        self.mask |= 1 << channel | 0

    def enableAll(self):
        self.mask = 0xffffffff | 0

    def toggle( self, channel ):
        self.mask ^= 1 << channel | 0

    def disable( self, channel ):
        self.mask &= ~ ( 1 << channel | 0 )

    def disableAll(self):
        self.mask = 0

    def test( self, layers ):
        return ( self.mask & layers.mask ) != 0

    def isEnabled( self, channel ):
        return ( self.mask & ( 1 << channel | 0 ) ) != 0
