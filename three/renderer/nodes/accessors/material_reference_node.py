#from three.renderer.nodes import ReferenceNode
from .reference_node import ReferenceNode

class MaterialReferenceNode(ReferenceNode):

    def __init__(self, property, inputType, material = None) -> None:
        super().__init__(property, inputType, material )
        self.material =  material

    def update( self, frame ):
        self.object = self.material if self.material else frame.material
        super().update( frame )
