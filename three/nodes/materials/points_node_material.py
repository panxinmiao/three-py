
from .node_material import NodeMaterial
from three.materials import PointsMaterial

defaultValues = PointsMaterial()
class PointsNodeMaterial(NodeMaterial):

    def __init__(self, parameters=None) -> None:
        super().__init__()

        self.transparent = True

        self.colorNode = None
        self.opacityNode = None

        self.alphaTestNode = None

        self.lightsNode = None

        self.sizeNode = None

        self.positionNode = None

        self.setDefaultValues( defaultValues )
        self.setValues( parameters )

    def copy( self, source ):

        self.colorNode = source.colorNode
        self.opacityNode = source.opacityNode

        self.alphaTestNode = source.alphaTestNode

        self.lightsNode = source.lightsNode

        self.sizeNode = source.sizeNode

        self.positionNode = source.positionNode

        return super().copy( source )
