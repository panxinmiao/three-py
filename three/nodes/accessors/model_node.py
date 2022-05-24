from .object3d_node import Object3DNode

class ModelNode(Object3DNode):
    def __init__(self, scope = Object3DNode.VIEW_MATRIX ) -> None:
        super().__init__(scope=scope)

    def update(self, frame):
        self.object3d = frame.object
        super().update(frame)