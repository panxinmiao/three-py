#from ...nodes import Object3DNode, Matrix4Node
from .object3d_node import Object3DNode

#from three.renderer.nodes import Object3DNode, Matrix4Node

class CameraNode(Object3DNode):
    PROJECTION_MATRIX = 'projectionMatrix'

    def __init__(self, scope = Object3DNode.POSITION) -> None:
        super().__init__(scope=scope)

    def getNodeType( self, builder ):
        scope = self.scope
        if scope == CameraNode.PROJECTION_MATRIX:
            return 'mat4'
        return super().getNodeType( builder )

    def update( self, frame ):
        camera = frame.camera
        uniformNode = self._uniformNode 
        scope = self.scope

        if scope == CameraNode.PROJECTION_MATRIX:
            uniformNode.value = camera.projectionMatrix

        elif scope == CameraNode.VIEW_MATRIX:
            uniformNode.value = camera.matrixWorldInverse

        else:
            self.object3d = camera
            super().update( frame )


    def generate( self, builder ):
        scope = self.scope
        if scope == CameraNode.PROJECTION_MATRIX:
            self._uniformNode.nodeType = 'mat4'

        return super().generate( builder )

