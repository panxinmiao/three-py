class UIEvent:
    def __init__(self, kwargs):
        #self.type = type
        self.__dict__.update(kwargs)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.__dict__}>"

    @property
    def eventType(self):
        return self.event_type

    @property
    def ctrlKey(self):
        return 'Ctrl' in self.modifiers

    @property
    def shiftKey(self):
        return 'Shift' in self.modifiers

    @property
    def metaKey(self):
        return 'Meta' in self.modifiers

    @property
    def pointerId(self):
        return self.ntouches

    @property
    def pointerType(self):
        return 'mouse'

    def get(self, name):
        return self.__dict__.get(name)

    def __getitem__(self, name):
        return self.__dict__.get(name)
