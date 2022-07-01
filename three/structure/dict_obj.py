# TODO: improve it
class Dict(dict):
    ''' TODO all dict method '''

    #__setattr__ = dict.__setitem__
    #__getattr__ = dict.__getitem__
    __repr__ = dict.__repr__

    def __init__(self, dict_obj = None):
        if dict_obj and isinstance(dict_obj, dict):
            for k,v in dict_obj.items():
                self.__setattr__ (k, v)


    def __setattr__(self, __name: str, __value) -> None:
        if isinstance(__value, dict):
            super().__setitem__(__name, Dict(__value))
        elif isinstance(__value, list):
            super().__setitem__(__name, [ Dict(v) if isinstance(v, dict) else v for v in __value ])
        else:
            super().__setitem__(__name, __value)
    
    def __getattr__(self ,name):
        return super().get(name, None)
        
    def __getitem__(self ,name):
        return super().get(name, None)

    def __delattr__(self, __name: str) -> None:
        return super().__delitem__(__name)

    def copy(self):
        return Dict(super().copy())

        

