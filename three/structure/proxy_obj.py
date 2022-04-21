
class Proxy:

    def __init__(self, obj, handler = {}) -> None:
        
        self.object = obj

        self.handler = handler

        self._get = handler.get('get', None)

    

    def __getattribute__(self, __name: str):
        get = object.__getattribute__(self, '_get')
        if get:
            return get(object.__getattribute__(self, 'object'), __name)
        else:
            return super().__getattribute__(__name)

