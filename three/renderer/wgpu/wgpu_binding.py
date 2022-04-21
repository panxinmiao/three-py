from ...structure import NoneAttribute

class WgpuBinding(NoneAttribute):

    def __init__(self, name="") -> None:
        self.name = name
        self.visibility = None

        self.type = None  # read-only

        self.isShared = False

    
    def setVisibility( self, visibility ):
        self.visibility = visibility