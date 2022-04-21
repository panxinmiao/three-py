from ..structure import NoneAttribute
class Event(NoneAttribute):

    def __init__(self, type, target = None):
        super().__init__()
        self._type = type
        self.target = target

    @property
    def type(self):
        return self._type