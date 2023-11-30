# TODO: how to remove it?
class NoneAttribute:
    def __getattr__(self, name:str):
        # cache attribute
        # setattr(self, name, None)
        self.__dict__[name] = None
        return None

    def __hash__(self) -> int:
        return id(self)