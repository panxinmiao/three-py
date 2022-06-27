def _isSubType(cls_name:str, cls: type):
    if cls_name == cls.__name__ or 'Wgpu'+cls_name == cls.__name__:
        return True
    
    for base in cls.__bases__: 
        if _isSubType(cls_name, base):
            return True

    return False

# TODO: how to remove it?
class NoneAttribute:
    def __getattr__(self, name:str):
        # cache attribute
        setattr(self, name, None)
        return None

    def __hash__(self) -> int:
        return id(self)