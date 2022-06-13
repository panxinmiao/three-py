from .reference_node import ReferenceNode

class UserDataNode(ReferenceNode):

    def __init__(self,  property, inputType, userData=None) -> None:
        super().__init__(property, inputType, userData)
        self.userData = userData


    def update(self, frame):
        self.object = self.userData if self.userData else frame.object.userData
        super().update(frame)
    
