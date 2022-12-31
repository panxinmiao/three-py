
from .node_material import NodeMaterial
from three.materials import LineBasicMaterial

defaultValues = LineBasicMaterial()

class LineBasicNodeMaterial(NodeMaterial):

    isLineBasicNodeMaterial = True

    def __init__(self, parameters = None) -> None:
        super().__init__()

        self.lights = False
        self.normals = False

        self.colorNode = None
        self.opacityNode = None

        self.alphaTestNode = None

        self.lightsNode = None

        self.positionNode = None

        self.setDefaultValues( defaultValues )

        self.setValues( parameters )

    def copy( self, source ):

        self.colorNode = source.colorNode
        self.opacityNode = source.opacityNode

        self.alphaTestNode = source.alphaTestNode

        self.lightsNode = source.lightsNode

        self.positionNode = source.positionNode

        return super().copy( source )
