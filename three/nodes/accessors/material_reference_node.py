from .reference_node import ReferenceNode

class MaterialReferenceNode(ReferenceNode):

    def __init__(self, property, inputType, material = None) -> None:
        super().__init__(property, inputType, material )
        self.material =  material

    def construct( self, builder ):
        material = self.material or builder.material
        
        self.node.value = getattr( material, self.property )

        return super().construct( builder )


    def update( self, frame ):
        self.object = self.material if self.material else frame.material
        super().update( frame )
