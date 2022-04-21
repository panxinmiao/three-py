def _isSubType(cls_name:str, cls: type):
    if cls_name == cls.__name__:
        return True
    
    #print("class__bases__", cls.__bases__)
    for base in cls.__bases__: 
        if _isSubType(cls_name, base):
            return True

    return False

class NoneAttribute:
    def __getattr__(self, name:str):
        # TODO someway better?
        if name.startswith('is'):
            cls_name = name[2:]
            return _isSubType(cls_name, self.__class__)
            # if cls_name == self.__class__.__name__:
            #     return True
            # else:
            # cls = getattr(three, cls_name, None)
            # if cls and isinstance(self, cls):
            #     return True
            # else:
            #     if name == f'is{self.__class__.__name__}':
            #         return True

            #     for base in self.__class__.__bases__:
            #         if name == f'is{base.__name__}':
            #             return True
            #     return False

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