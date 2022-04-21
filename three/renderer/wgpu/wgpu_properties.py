from weakref import WeakKeyDictionary
from ...structure import Dict

class WgpuProperties:

    def __init__(self) -> None:
        
        self.properties = WeakKeyDictionary()

    def get(self, object ):

        map = self.properties.get( object )

        if map is None:
            map = Dict({})
            self.properties[object] = map

        return map


    def remove( self, object ):
        self.properties.pop( object )


    def dispose( self ):
        self.properties = WeakKeyDictionary()
