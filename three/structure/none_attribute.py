def _isSubType(cls_name:str, cls: type):
    if cls_name == cls.__name__ or 'Wgpu'+cls_name == cls.__name__:
        return True
    
    for base in cls.__bases__: 
        if _isSubType(cls_name, base):
            return True

    return False

class NoneAttribute:
    def __getattr__(self, name:str):
        # TODO remove this for performance
        if name.startswith('is'):
            cls_name = name[2:]
            return _isSubType(cls_name, self.__class__)
        return None

    @property
    def type(self):
        if hasattr(self, '_type'):
            return self._type
        return self.__class__.__name__

    @type.setter
    def type(self, type):
        self._type = type


    def __hash__(self) -> int:
        return id(self)