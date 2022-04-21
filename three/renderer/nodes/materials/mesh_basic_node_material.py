from .node_material import NodeMaterial
from ....materials import MeshBasicMaterial

defaultValues = MeshBasicMaterial()

class MeshBasicNodeMaterial(NodeMaterial):
    def __init__(self, parameters ) -> None:
        super().__init__()
        self.lights = True
        self.colorNode = None
        self.opacityNode = None
        self.alphaTestNode = None
        self.lightNode = None
        self.positionNode = None

        self.setDefaultValues( defaultValues )
        self.setValues( parameters )

    def copy( self, source ):
        self.colorNode = source.colorNode
        self.opacityNode = source.opacityNode
        self.alphaTestNode = source.alphaTestNode
        self.lightNode = source.lightNode
        self.positionNode = source.positionNode
        return super().copy( source )